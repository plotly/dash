#!/usr/bin/env node
if (process.env.MODULES_PATH) {
    module.paths.push(process.env.MODULES_PATH);
}
const ts = require('typescript');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const src = args[2];
const ignorePattern = args[0] ? new RegExp(args[0]) : null;
const reservedPattern = args[1] ? new RegExp(args[1]) : null;

let failedBuild = false;

const isOptional = prop => (prop.getFlags() & ts.SymbolFlags.Optional) !== 0;

const logError = error => process.stderr.write(error + '\n');

const isReservedPropName = propName => {
    if (reservedPattern.test(propName)) {
        failedBuild = true;
        logError(
            `\nERROR: "${propName}" matches reserved word 
            pattern: ${reservedPattern.toString()}`
        );
        return true;
    }
    return false;
};

const PRIMITIVES = [
    'string',
    'number',
    'bool',
    'any',
    'array',
    'object',
    'node'
];

const unionSupport = PRIMITIVES.concat('boolean', 'Element');

const reArray = new RegExp(`(${unionSupport.join('|')})\\[\\]`);

const isArray = rawType => reArray.test(rawType);

const isUnionlitteral = typeObj =>
    typeObj.types.every(
        t =>
            t.getFlags() &
            (ts.TypeFlags.StringLiteral |
                ts.TypeFlags.NumberLiteral |
                ts.TypeFlags.EnumLiteral |
                ts.TypeFlags.Undefined)
    );

let tsconfig = {};

if (fs.existsSync('tsconfig.json')) {
    tsconfig = JSON.parse(fs.readFileSync('tsconfig.json'));
}

function zipArrays(...arrays) {
    const arr = [];
    for (let i = 0; i <= arrays[0].length - 1; i++) {
        arr.push(arrays.map(a => a[i]));
    }
    return arr;
}

function gatherComponents(directory, components = {}) {
    const names = [];
    const filepaths = [];

    fs.readdirSync(src).forEach(f => {
        const filepath = path.join(directory, f);
        if (fs.lstatSync(filepath).isDirectory()) {
            gatherComponents(f, components);
        } else {
            if (!filepath.endsWith(".tsx")) {
                return;
            }
            try {
                filepaths.push(filepath);
                const name = /(.*)\.tsx/.exec(f)[1];
                if (ignorePattern) {
                    if (!ignorePattern.test(name)) {
                        names.push(name);
                    }
                } else {
                    names.push(name);
                }
            } catch (err) {
                process.stderr.write(
                    `ERROR: Invalid component file ${filepath}: ${err}`
                );
            }
        }
    });

    const program = ts.createProgram(filepaths, tsconfig);
    const checker = program.getTypeChecker();

    const coerceValue = t => {
        // May need to improve for shaped/list literals.
        if (t.isStringLiteral()) return `'${t.value}'`;
        return t.value;
    };

    const getComponentFromExport = exp => {
        const decl = exp.valueDeclaration || exp.declarations[0];
        const type = checker.getTypeOfSymbolAtLocation(exp, decl);
        const typeSymbol = type.symbol || type.aliasSymbol;

        if (!typeSymbol) {
            return exp;
        }

        const symbolName = typeSymbol.getName();

        if (
            (symbolName === 'MemoExoticComponent' ||
                symbolName === 'ForwardRefExoticComponent') &&
            exp.valueDeclaration &&
            ts.isExportAssignment(exp.valueDeclaration) &&
            ts.isCallExpression(exp.valueDeclaration.expression)
        ) {
            const component = checker.getSymbolAtLocation(
                exp.valueDeclaration.expression.arguments[0]
            );

            if (component) return component;
        }
        return exp;
    };

    const getParent = node => {
        let parent = node;
        while (parent.parent) {
            if (parent.parent.kind === ts.SyntaxKind.SourceFile) {
                // We want the parent before the source file.
                break;
            }
            parent = parent.parent;
        }
        return parent;
    };

    const getEnum = typeObj => ({
        name: 'enum',
        value: typeObj.types.map(t => ({
            value: coerceValue(t),
            computed: false
        }))
    });

    const getUnion = (typeObj, propObj) => {
        let name = 'union',
            value;
        // Union only do base types
        value = typeObj.types
            .filter(t => {
                let typeName = t.intrinsicName;
                if (!typeName) {
                    if (t.members) {
                        typeName = 'object';
                    }
                }
                return (
                    unionSupport.includes(typeName) ||
                    isArray(checker.typeToString(t))
                );
            })
            .map(t => getPropType(t, propObj));

        if (!value.length) {
            name = 'any';
            value = undefined;
        }
        return {
            name,
            value
        };
    };

    const getPropTypeName = propName => {
        if (propName.includes('=>') || propName === 'Function') {
            return 'func';
        } else if (propName === 'boolean') {
            return 'bool';
        } else if (propName === '[]') {
            return 'array';
        } else if (
            propName === 'Element' ||
            propName === 'ReactNode' ||
            propName === 'ReactElement'
        ) {
            return 'node';
        }
        return propName;
    };

    const getPropType = (propType, propObj) => {
        // Types can get namespace prefixes or not.
        let name = checker.typeToString(propType).replace(/^React\./, '');
        let value;
        const raw = name;

        if (propType.isUnion()) {
            if (isUnionlitteral(propType)) {
                return {...getEnum(propType), raw};
            } else if (raw.includes('|')) {
                return {...getUnion(propType, propObj), raw};
            }
        }

        name = getPropTypeName(name);

        // Shapes & array support.
        if (!PRIMITIVES.concat('enum', 'func', 'union').includes(name)) {
            if (
                name.includes('[]') ||
                name.includes('Array') ||
                name === 'tuple'
            ) {
                name = 'arrayOf';
                const replaced = raw.replace('[]', '');
                if (unionSupport.includes('replaced')) {
                    // Simple types are easier.
                    value = {
                        name: getPropTypeName(replaced),
                        raw: replaced
                    };
                } else {
                    // Complex types get the type parameter (Array<type>)
                    const [nodeType] = checker.getTypeArguments(propType);

                    if (nodeType) {
                        value = getPropType(nodeType, propObj);
                    } else {
                        // Not sure, might be unsupported here.
                        name = 'array';
                    }
                }
            } else {
                name = 'shape';
                // If the type is declared as union it will have a types attribute.
                if (propType.types && propType.types.length) {
                    if (isUnionlitteral(propType)) {
                        return {...getEnum(propType), raw};
                    }
                    return {...getUnion(propType, propObj), raw};
                }

                value = getProps(
                    checker.getPropertiesOfType(propType),
                    propObj,
                    [],
                    {},
                    true
                );
            }
        }

        return {
            name,
            value,
            raw
        };
    };

    const getDefaultProps = (symbol, source) => {
        const statements = source.statements.filter(
            stmt =>
                (!!stmt.name &&
                    checker.getSymbolAtLocation(stmt.name) === symbol) ||
                ts.isExpressionStatement(stmt) ||
                ts.isVariableStatement(stmt)
        );
        return statements.reduce((acc, statement) => {
            let propMap = {};

            statement.getChildren().forEach(child => {
                let {right} = child;
                if (right && ts.isIdentifier(right)) {
                    const value = source.locals.get(right.escapedText);
                    if (
                        value &&
                        value.valueDeclaration &&
                        ts.isVariableDeclaration(value.valueDeclaration) &&
                        value.valueDeclaration.initializer
                    ) {
                        right = value.valueDeclaration.initializer;
                    }
                }
                if (right) {
                    const {properties} = right;
                    if (properties) {
                        propMap = getDefaultPropsValues(properties);
                    }
                }
            });

            return {
                ...acc,
                ...propMap
            };
        }, {});
    };

    const getPropComment = symbol => {
        // Doesn't work too good with the JsDocTags losing indentation.
        // But used only in props should be fine.
        const comment = symbol.getDocumentationComment();
        const tags = symbol.getJsDocTags();
        if (comment && comment.length) {
            return comment
                .map(c => c.text)
                .concat(
                    tags.map(t =>
                        ['@', t.name].concat((t.text || []).map(e => e.text))
                    )
                )
                .join('\n');
        }
        return '';
    };

    const getPropsForFunctionalComponent = type => {
        const callSignatures = type.getCallSignatures();

        for (const sig of callSignatures) {
            const params = sig.getParameters();
            if (params.length === 0) {
                continue;
            }

            // There is only one parameter for functional components: props
            const p = params[0];
            if (p.name === 'props' || params.length === 1) {
                return p;
            }
        }
        return null;
    };

    const getPropsForClassComponent = (typeSymbol, source, defaultProps) => {
        const childs = source.getChildAt(0);
        let stop;

        for (let i = 0, n = childs.getChildCount(); i < n && !stop; i++) {
            const c = childs.getChildAt(i);
            if (!ts.isClassDeclaration(c)) continue;

            if (!c.heritageClauses) continue;

            for (const clause of c.heritageClauses) {
                if (clause.token !== ts.SyntaxKind.ExtendsKeyword) continue;
                const t = clause.types[0];
                const propType = t.typeArguments[0];

                const type = checker.getTypeFromTypeNode(propType);

                return getProps(
                    type.getProperties(),
                    typeSymbol,
                    [],
                    defaultProps
                );
            }
        }
    };

    const getDefaultPropsValues = properties =>
        properties.reduce((acc, p) => {
            if (!p.name || !p.initializer) {
                return acc;
            }
            let propName, value;

            switch (p.name.kind) {
                case ts.SyntaxKind.NumericLiteral:
                case ts.SyntaxKind.StringLiteral:
                case ts.SyntaxKind.Identifier:
                    propName = p.name.text;
                    break;
                case ts.SyntaxKind.ComputedPropertyName:
                    propName = p.name.getText();
                    break;
            }

            const {initializer} = p;

            switch (initializer.kind) {
                case ts.SyntaxKind.StringLiteral:
                    value = `'${initializer.text}'`;
                    break;
                case ts.SyntaxKind.NumericLiteral:
                    value = initializer.text;
                    break;
                case ts.SyntaxKind.NullKeyword:
                    value = 'null';
                    break;
                case ts.SyntaxKind.FalseKeyword:
                    value = 'false';
                    break;
                case ts.SyntaxKind.TrueKeyword:
                    value = 'true';
                    break;
                default:
                    try {
                        value = initializer.getText();
                    } catch (e) {
                        value = undefined;
                    }
            }

            acc[propName] = {value, computed: false};

            return acc;
        }, {});

    const getDefaultPropsForClassComponent = (type, source) => {
        // For class component, the type has its own property, then get the
        // first declaration and one of them will be either
        // an ObjectLiteralExpression or an Identifier which get in the
        // newChild with the proper props.
        const defaultProps = type.getProperty('defaultProps');
        if (!defaultProps) {
            return {};
        }
        const decl = defaultProps.getDeclarations()[0];
        let propValues = {};

        decl.getChildren().forEach(child => {
            let newChild = child;

            if (ts.isIdentifier(child)) {
                // There should be two identifier, the first is ignored.
                const value = source.locals.get(child.escapedText);
                if (
                    value &&
                    value.valueDeclaration &&
                    ts.isVariableDeclaration(value.valueDeclaration) &&
                    value.valueDeclaration.initializer
                ) {
                    newChild = value.valueDeclaration.initializer;
                }
            }

            const {properties} = newChild;
            if (properties) {
                propValues = getDefaultPropsValues(properties);
            }
        });
        return propValues;
    };

    const getProps = (
        properties,
        propsObj,
        baseProps = [],
        defaultProps = {},
        flat = false
    ) => {
        const results = {};

        properties.forEach(prop => {
            const name = prop.getName();
            if (isReservedPropName(name)) {
                return;
            }
            const propType = checker.getTypeOfSymbolAtLocation(
                prop,
                propsObj.valueDeclaration
            );
            const baseProp = baseProps.find(p => p.getName() === name);
            const defaultValue = defaultProps[name];

            const required =
                !isOptional(prop) &&
                (!baseProp || !isOptional(baseProp)) &&
                defaultValue === undefined;

            const description = getPropComment(prop);

            let result = {
                description,
                required,
                defaultValue
            };
            const type = getPropType(propType, propsObj);
            // root object is inserted as type,
            // otherwise it's flat in the value prop.
            if (!flat) {
                result.type = type;
            } else {
                result = {...result, ...type};
            }

            results[name] = result;
        });

        return results;
    };

    const getPropInfo = (propsObj, defaultProps) => {
        const propsType = checker.getTypeOfSymbolAtLocation(
            propsObj,
            propsObj.valueDeclaration
        );
        const baseProps = propsType.getApparentProperties();
        let propertiesOfProps = baseProps;

        if (propsType.isUnionOrIntersection()) {
            propertiesOfProps = [
                ...checker.getAllPossiblePropertiesOfTypes(propsType.types),
                ...baseProps
            ];

            if (!propertiesOfProps.length) {
                const subTypes = checker.getAllPossiblePropertiesOfTypes(
                    propsType.types.reduce(
                        (all, t) => [...all, ...(t.types || [])],
                        []
                    )
                );
                propertiesOfProps = [...subTypes, ...baseProps];
            }
        }

        return getProps(propertiesOfProps, propsObj, baseProps, defaultProps);
    };

    zipArrays(filepaths, names).forEach(([f, name]) => {
        const source = program.getSourceFile(f);
        const moduleSymbol = checker.getSymbolAtLocation(source);
        const exports = checker.getExportsOfModule(moduleSymbol);

        exports.forEach(exp => {
            let rootExp = getComponentFromExport(exp);
            const declaration =
                rootExp.valueDeclaration || rootExp.declarations[0];
            const type = checker.getTypeOfSymbolAtLocation(
                rootExp,
                declaration
            );

            let commentSource = rootExp;
            const typeSymbol = type.symbol || type.aliasSymbol;
            const originalName = rootExp.getName();

            if (!rootExp.valueDeclaration) {
                if (
                    originalName === 'default' &&
                    !typeSymbol &&
                    (rootExp.flags & ts.SymbolFlags.Alias) !== 0
                ) {
                    // Some type of Exotic?
                    commentSource =
                        checker.getAliasedSymbol(
                            commentSource
                        ).valueDeclaration;
                } else if (!typeSymbol) {
                    // Invalid component
                    return null;
                } else {
                    // Function components.
                    rootExp = typeSymbol;
                    commentSource = rootExp.valueDeclaration;
                    if (
                        rootExp.valueDeclaration &&
                        rootExp.valueDeclaration.parent
                    ) {
                        // Function with export later like `const MyComponent = (props) => <></>;`
                        commentSource = getParent(
                            rootExp.valueDeclaration.parent
                        );
                    }
                }
            } else if (
                type.symbol &&
                (ts.isPropertyAccessExpression(declaration) ||
                    ts.isPropertyDeclaration(declaration))
            ) {
                commentSource = type.symbol.declarations[0];
            }

            if (commentSource.valueDeclaration) {
                commentSource = commentSource.valueDeclaration; // class components
                if (
                    commentSource.parent &&
                    commentSource.parent.kind !== ts.SyntaxKind.SourceFile
                ) {
                    // Memo components
                    commentSource = commentSource.parent;
                }
            }

            let defaultProps = getDefaultProps(typeSymbol, source);
            const propsType = getPropsForFunctionalComponent(type);
            const isContext = !!type.getProperty('isContext');

            let props;

            if (propsType) {
                props = getPropInfo(propsType, defaultProps);
            } else {
                defaultProps = getDefaultPropsForClassComponent(type, source);
                props = getPropsForClassComponent(
                    typeSymbol,
                    source,
                    defaultProps
                );
            }

            const fullText = source.getFullText();
            let description;
            const commentRanges = ts.getLeadingCommentRanges(
                fullText,
                commentSource.getFullStart()
            );
            if (commentRanges && commentRanges.length) {
                description = commentRanges
                    .map(r =>
                        fullText
                            .slice(r.pos + 4, r.end - 3)
                            .split('\n')
                            .map(s => s.slice(3, s.length))
                            .filter(e => e)
                            .join('\n')
                    )
                    .join('');
            }

            components[name] = {
                displayName: name,
                description,
                props,
                isContext
            };
        });
    });

    return components;
}

const metadata = gatherComponents(src);
if (!failedBuild) {
    process.stdout.write(JSON.stringify(metadata, null, 2));
} else {
    logError('Extracting props info failed');
    process.exit(1);
}
