import child_process from 'child_process';
import path from 'path';
import R from 'ramda';

function getMetadata() {
    return new Promise((resolve, reject) => {
        const cp = child_process.spawn(
            process.execPath,
            [
                path.resolve(__dirname, '..', '..', 'dash', 'extract-meta.js'),
                '""', // ignore pattern
                '^_.*$', // reserved keywords
                path.join(__dirname, 'src', 'components')
            ],
            {
                env: {MODULES_PATH: path.resolve(__dirname, './node_modules'), ...process.env},
                cwd: __dirname
            }
        );
        const meta = [];
        const err = [];
        cp.stdout.on('data', data => {
            meta.push(data);
        });
        cp.stderr.on('data', data => {
            err.push(data);
        });
        cp.on('close', code => {
            if (code === 0) {
                resolve(
                    R.values(JSON.parse(meta.join(''))).reduce((acc, c) => {
                        // Map them back to component name for easier access.
                        acc[c.displayName] = c;
                        return acc;
                    }, {})
                );
            } else {
                reject(err.join(''));
            }
        });
        cp.on('error', error => {
            console.error(error);
            reject(error);
        });
    });
}

describe('Test Typescript component metadata generation', () => {
    let metadata;

    beforeAll(async () => {
        metadata = await getMetadata();
    });

    const propPath = (componentName, propName) => [
        componentName,
        'props',
        propName
    ];

    describe.each([
        'TypeScriptComponent',
        'TypeScriptClassComponent',
        'MemoTypeScriptComponent',
        'FCComponent',
    ])('Test prop type names', componentName => {
        const getPropTypeName = (name, data) =>
            R.path(propPath(componentName, name).concat('type', 'name'), data);
        const testTypeFactory = (name, expectedType) => () =>
            expect(getPropTypeName(name, metadata)).toBe(expectedType);

        test(
            `${componentName} string type`,
            testTypeFactory('a_string', 'string')
        );
        test(
            `${componentName} number type`,
            testTypeFactory('a_number', 'number')
        );
        test(
            `${componentName} array type`,
            testTypeFactory('array_string', 'arrayOf')
        );
        test(`${componentName} object type`, testTypeFactory('obj', 'shape'));
        test(`${componentName} union type`, testTypeFactory('union', 'union'));
        test(
            `${componentName} enum type`,
            testTypeFactory('enum_string', 'enum')
        );
        test(
            `${componentName} children React.Node`,
            testTypeFactory('children', 'node')
        );
        test(
            `${componentName} element JSX.Element`,
            testTypeFactory('element', 'node')
        );
        test(
            `${componentName} boolean type`,
            testTypeFactory('a_bool', 'bool')
        );
        test(
            `${componentName} setProps func`,
            testTypeFactory('setProps', 'func')
        );
        test(
            `${componentName} tuple tuple`,
            testTypeFactory('a_tuple', 'tuple')
        );
        test(
            `${componentName} object of string`,
            testTypeFactory('object_of_string', 'objectOf')
        );
        test(
            `${componentName} object of components`,
            testTypeFactory('object_of_components', 'objectOf')
        );
    });

    describe('Test prop attributes', () => {
        test('Required props', () => {
            expect(
                R.path(
                    propPath('TypeScriptComponent', 'required_string').concat(
                        'required'
                    ),
                    metadata
                )
            ).toBeTruthy();
            expect(
                R.path(
                    propPath('TypeScriptComponent', 'a_string').concat(
                        'required'
                    ),
                    metadata
                )
            ).toBeFalsy();
        });
        test('Component prop has comment', () => {
            // Comments with `@` in them will not work due the way the typescript compiler handle them with jsdoc.
            // To fix & add test once they add back the ability to get raw comments.
            expect(
                R.path(
                    propPath('TypeScriptComponent', 'required_string').concat(
                        'description'
                    ),
                    metadata
                )
            ).toBe('A string');
        });
        test('Enum options', () => {
            expect(
                R.path(
                    propPath('TypeScriptComponent', 'enum_string').concat(
                        'type',
                        'value'
                    ),
                    metadata
                )
            ).toStrictEqual([
                {value: "'one'", computed: false},
                {value: "'two'", computed: false}
            ]);
        });
        test('Union of number and string', () => {
            const propType = R.path(
                propPath('TypeScriptComponent', 'union').concat('type'),
                metadata
            );
            expect(propType.value.map(R.prop('name'))).toStrictEqual([
                'string',
                'number'
            ]);
        });
        test('Union of shape and string', () => {
            const propType = R.path(
                propPath('TypeScriptComponent', 'union_shape').concat(
                    'type',
                    'value'
                ),
                metadata
            );
            const types = propType.map(R.prop('name'));
            expect(types).toHaveLength(2);
            expect(types).toContainEqual('shape');
            expect(types).toContainEqual('string');
        });
        test('Array of union of shapes and string', () => {
            const propType = R.path(
                propPath('TypeScriptComponent', 'array_union_shape').concat(
                    'type'
                ),
                metadata
            );
            expect(propType.value.name).toBe('union');
            expect(propType.value.value.length).toBe(2);
            expect(propType.value.value[0].name).toBe('string');
            expect(propType.value.value[1].name).toBe('shape');
        });
        test('Obj properties', () => {
            const propType = R.path(
                propPath('TypeScriptComponent', 'obj').concat('type', 'value'),
                metadata
            );
            expect(propType.value.name).toBe('any');
            expect(propType.label.name).toBe('string');
        });
        test.each(['TypeScriptComponent', 'TypeScriptClassComponent'])(
            'Default props',
            (componentName: string) => {
                const defaultValue = (field: string) =>
                    R.path(
                        propPath(componentName, field).concat(
                            'defaultValue',
                            'value'
                        ),
                        metadata
                    );
                expect(defaultValue('string_default')).toBe("'default'");
                expect(defaultValue('number_default')).toBe('42');
                expect(defaultValue('bool_default')).toBe(
                    componentName === 'TypeScriptComponent' ? 'true' : 'false'
                );
                expect(defaultValue('null_default')).toBe('null');
                expect(eval(`(${defaultValue('obj_default')})`)).toStrictEqual({
                    a: 'a',
                    b: 3
                });
            }
        );

        test(
            'Nested props to any', () => {
                expect(
                    R.path([
                        'TypeScriptComponent',
                        'props',
                        'nested',
                        'type',
                        'value',
                        'nested',
                        'name'
                    ], metadata)).toBe('any')
            }
        );

        test(
            'Tuple elements', () => {
                const tuplePath: (string|number)[] = [
                    'TypeScriptComponent',
                    'props',
                    'a_tuple',
                    'type',
                    'elements'
                ]
                expect(
                    R.path(tuplePath.concat(0, 'name'), metadata)
                ).toBe('number');
                expect(
                    R.path(tuplePath.concat(1, 'name'), metadata)
                ).toBe('string');
            }
        );

        test(
            'objectOf node', () => {
                const objectOfComponents = R.path(
                    propPath("TypeScriptComponent", "object_of_components")
                        .concat(["type", "value", "name"]),
                    metadata
                );
                expect(objectOfComponents).toBe("node");
            }
        )
    });

    describe('Test component comments', () => {
        test('Component has docstring', () => {
            expect(
                R.path(['TypeScriptComponent', 'description'], metadata)
            ).toBe('Component docstring');
        });
        test.each(['TypeScriptClassComponent', 'MemoTypeScriptComponent'])(
            'Component with `@` in docstring',
            componentName => {
                expect(R.path([componentName, 'description'], metadata)).toBe(
                    'Description\n' +
                        'Example:\n```\n' +
                        '@app.callback(...)\n' +
                        'def on_click(*args):\n' +
                        '    return 1\n' +
                        '```'
                );
            }
        );
    });
    describe('Test mixed generation', () => {
        test('Standard js component is parsed', () => {
            expect(R.path(['StandardComponent'], metadata)).toBeDefined();
        });
        test('Mixed component prop-type & typescript', () => {
            expect(R.path(['MixedComponent', 'props', 'prop', 'type', 'name'], metadata)).toBe('arrayOf')
        })
    });
    describe('Test special cases', () => {
        test('Component with picked boolean prop', () => {
            expect(R.path(['WrappedHTML', "props", "autoFocus", "type", "name"], metadata)).toBe("bool");
        });
        test('Empty Component', () => {
            expect(R.path(['EmptyComponent', 'props'], metadata)).toBeDefined();
        });
    });
});
