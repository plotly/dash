import {DepGraph} from 'dependency-graph';
import isNumeric from 'fast-isnumeric';
import {
    all,
    any,
    ap,
    assoc,
    difference,
    equals,
    evolve,
    findIndex,
    flatten,
    forEachObjIndexed,
    includes,
    intersection,
    isEmpty,
    keys,
    map,
    mergeRight,
    path,
    pluck,
    props,
    startsWith,
    values,
    zip,
    zipObj
} from 'ramda';

import {
    combineIdAndProp,
    getCallbacksByInput,
    getPriority,
    INDIRECT,
    mergeMax,
    makeResolvedCallback,
    resolveDeps
} from './dependencies_ts';
import {computePaths, getPath} from './paths';

import {crawlLayout} from './utils';

import Registry from '../registry';

/*
 * If this update is for multiple outputs, then it has
 * starting & trailing `..` and each propId pair is separated
 * by `...`, e.g.
 * "..output-1.value...output-2.value...output-3.value...output-4.value.."
 */
export const isMultiOutputProp = idAndProp => idAndProp.startsWith('..');

const ALL = {wild: 'ALL', multi: 1};
const MATCH = {wild: 'MATCH'};
const ALLSMALLER = {wild: 'ALLSMALLER', multi: 1, expand: 1};
const wildcards = {ALL, MATCH, ALLSMALLER};
const allowedWildcards = {
    Output: {ALL, MATCH},
    Input: wildcards,
    State: wildcards
};
const wildcardValTypes = ['string', 'number', 'boolean'];

const idInvalidChars = ['.', '{'];

/*
 * If this ID is a wildcard, it is a stringified JSON object
 * the "{" character is disallowed from regular string IDs
 */
const isWildcardId = idStr => idStr.startsWith('{');

/*
 * Turn stringified wildcard IDs into objects.
 * Wildcards are encoded as single-item arrays containing the wildcard name
 * as a string.
 */
function parseWildcardId(idStr) {
    return map(
        val => (Array.isArray(val) && wildcards[val[0]]) || val,
        JSON.parse(idStr)
    );
}

/*
 * If this update is for multiple outputs, then it has
 * starting & trailing `..` and each propId pair is separated
 * by `...`, e.g.
 * "..output-1.value...output-2.value...output-3.value...output-4.value.."
 */
function parseMultipleOutputs(outputIdAndProp) {
    return outputIdAndProp.substr(2, outputIdAndProp.length - 4).split('...');
}

export function splitIdAndProp(idAndProp) {
    // since wildcard ids can have . in them but props can't,
    // look for the last . in the string and split there
    const dotPos = idAndProp.lastIndexOf('.');
    const idStr = idAndProp.substr(0, dotPos);
    return {
        id: parseIfWildcard(idStr),
        property: idAndProp.substr(dotPos + 1)
    };
}

/*
 * Check if this ID is a stringified object, and if so parse it to that object
 */
export function parseIfWildcard(idStr) {
    return isWildcardId(idStr) ? parseWildcardId(idStr) : idStr;
}

/*
 * JSON.stringify - for the object form - but ensuring keys are sorted
 */
export function stringifyId(id) {
    if (typeof id !== 'object') {
        return id;
    }
    const stringifyVal = v => (v && v.wild) || JSON.stringify(v);
    const parts = Object.keys(id)
        .sort()
        .map(k => JSON.stringify(k) + ':' + stringifyVal(id[k]));
    return '{' + parts.join(',') + '}';
}

/*
 * id dict values can be numbers, strings, and booleans.
 * We need a definite ordering that will work across types,
 * even if sane users would not mix types.
 * - numeric strings are treated as numbers
 * - booleans come after numbers, before strings. false, then true.
 * - non-numeric strings come last
 */
function idValSort(a, b) {
    const bIsNumeric = isNumeric(b);
    if (isNumeric(a)) {
        if (bIsNumeric) {
            const aN = Number(a);
            const bN = Number(b);
            return aN > bN ? 1 : aN < bN ? -1 : 0;
        }
        return -1;
    }
    if (bIsNumeric) {
        return 1;
    }
    const aIsBool = typeof a === 'boolean';
    if (aIsBool !== (typeof b === 'boolean')) {
        return aIsBool ? -1 : 1;
    }
    return a > b ? 1 : a < b ? -1 : 0;
}

/*
 * Provide a value known to be before or after v, according to idValSort
 */
const valBefore = v => (isNumeric(v) ? v - 1 : 0);
const valAfter = v => (typeof v === 'string' ? v + 'z' : 'z');

function addMap(depMap, id, prop, dependency) {
    const idMap = (depMap[id] = depMap[id] || {});
    const callbacks = (idMap[prop] = idMap[prop] || []);
    callbacks.push(dependency);
}

function addPattern(depMap, idSpec, prop, dependency) {
    const keys = Object.keys(idSpec).sort();
    const keyStr = keys.join(',');
    const values = props(keys, idSpec);
    const keyCallbacks = (depMap[keyStr] = depMap[keyStr] || {});
    const propCallbacks = (keyCallbacks[prop] = keyCallbacks[prop] || []);
    let valMatch = false;
    for (let i = 0; i < propCallbacks.length; i++) {
        if (equals(values, propCallbacks[i].values)) {
            valMatch = propCallbacks[i];
            break;
        }
    }
    if (!valMatch) {
        valMatch = {keys, values, callbacks: []};
        propCallbacks.push(valMatch);
    }
    valMatch.callbacks.push(dependency);
}

function validateDependencies(parsedDependencies, dispatchError) {
    const outStrs = {};
    const outObjs = [];

    parsedDependencies.forEach(dep => {
        const {inputs, outputs, state} = dep;
        let hasOutputs = true;
        if (outputs.length === 1 && !outputs[0].id && !outputs[0].property) {
            hasOutputs = false;
            dispatchError('A callback is missing Outputs', [
                'Please provide an output for this callback:',
                JSON.stringify(dep, null, 2)
            ]);
        }

        const head =
            'In the callback for output(s):\n  ' +
            outputs.map(combineIdAndProp).join('\n  ');

        if (!inputs.length) {
            dispatchError('A callback is missing Inputs', [
                head,
                'there are no `Input` elements.',
                'Without `Input` elements, it will never get called.',
                '',
                'Subscribing to `Input` components will cause the',
                'callback to be called whenever their values change.'
            ]);
        }

        const spec = [
            [outputs, 'Output'],
            [inputs, 'Input'],
            [state, 'State']
        ];
        spec.forEach(([args, cls]) => {
            if (cls === 'Output' && !hasOutputs) {
                // just a quirk of how we pass & parse outputs - if you don't
                // provide one, it looks like a single blank output. This is
                // actually useful for graceful failure, so we work around it.
                return;
            }

            if (!Array.isArray(args)) {
                dispatchError(`Callback ${cls}(s) must be an Array`, [
                    head,
                    `For ${cls}(s) we found:`,
                    JSON.stringify(args),
                    'but we expected an Array.'
                ]);
            }
            args.forEach((idProp, i) => {
                validateArg(idProp, head, cls, i, dispatchError);
            });
        });

        findDuplicateOutputs(outputs, head, dispatchError, outStrs, outObjs);
        findMismatchedWildcards(outputs, inputs, state, head, dispatchError);
    });
}

function validateArg({id, property}, head, cls, i, dispatchError) {
    if (typeof property !== 'string' || !property) {
        dispatchError('Callback property error', [
            head,
            `${cls}[${i}].property = ${JSON.stringify(property)}`,
            'but we expected `property` to be a non-empty string.'
        ]);
    }

    if (typeof id === 'object') {
        if (isEmpty(id)) {
            dispatchError('Callback item missing ID', [
                head,
                `${cls}[${i}].id = {}`,
                'Every item linked to a callback needs an ID'
            ]);
        }

        forEachObjIndexed((v, k) => {
            if (!k) {
                dispatchError('Callback wildcard ID error', [
                    head,
                    `${cls}[${i}].id has key "${k}"`,
                    'Keys must be non-empty strings.'
                ]);
            }

            if (typeof v === 'object' && v.wild) {
                if (allowedWildcards[cls][v.wild] !== v) {
                    dispatchError('Callback wildcard ID error', [
                        head,
                        `${cls}[${i}].id["${k}"] = ${v.wild}`,
                        `Allowed wildcards for ${cls}s are:`,
                        keys(allowedWildcards[cls]).join(', ')
                    ]);
                }
            } else if (!includes(typeof v, wildcardValTypes)) {
                dispatchError('Callback wildcard ID error', [
                    head,
                    `${cls}[${i}].id["${k}"] = ${JSON.stringify(v)}`,
                    'Wildcard callback ID values must be either wildcards',
                    'or constants of one of these types:',
                    wildcardValTypes.join(', ')
                ]);
            }
        }, id);
    } else if (typeof id === 'string') {
        if (!id) {
            dispatchError('Callback item missing ID', [
                head,
                `${cls}[${i}].id = "${id}"`,
                'Every item linked to a callback needs an ID'
            ]);
        }
        const invalidChars = idInvalidChars.filter(c => includes(c, id));
        if (invalidChars.length) {
            dispatchError('Callback invalid ID string', [
                head,
                `${cls}[${i}].id = '${id}'`,
                `characters '${invalidChars.join("', '")}' are not allowed.`
            ]);
        }
    } else {
        dispatchError('Callback ID type error', [
            head,
            `${cls}[${i}].id = ${JSON.stringify(id)}`,
            'IDs must be strings or wildcard-compatible objects.'
        ]);
    }
}

function findDuplicateOutputs(outputs, head, dispatchError, outStrs, outObjs) {
    const newOutputStrs = {};
    const newOutputObjs = [];
    outputs.forEach(({id, property}, i) => {
        if (typeof id === 'string') {
            const idProp = combineIdAndProp({id, property});
            if (newOutputStrs[idProp]) {
                dispatchError('Duplicate callback Outputs', [
                    head,
                    `Output ${i} (${idProp}) is already used by this callback.`
                ]);
            } else if (outStrs[idProp]) {
                dispatchError('Duplicate callback outputs', [
                    head,
                    `Output ${i} (${idProp}) is already in use.`,
                    'To resolve this, set `allow_duplicate=True` on',
                    'duplicate outputs, or combine the outputs into',
                    'one callback function, distinguishing the trigger',
                    'by using `dash.callback_context` if necessary.'
                ]);
            } else {
                newOutputStrs[idProp] = 1;
            }
        } else {
            const idObj = {id, property};
            const selfOverlap = wildcardOverlap(idObj, newOutputObjs);
            const otherOverlap = selfOverlap || wildcardOverlap(idObj, outObjs);
            if (selfOverlap || otherOverlap) {
                const idProp = combineIdAndProp(idObj);
                const idProp2 = combineIdAndProp(selfOverlap || otherOverlap);
                dispatchError('Overlapping wildcard callback outputs', [
                    head,
                    `Output ${i} (${idProp})`,
                    `overlaps another output (${idProp2})`,
                    `used in ${selfOverlap ? 'this' : 'a different'} callback.`
                ]);
            } else {
                newOutputObjs.push(idObj);
            }
        }
    });
    keys(newOutputStrs).forEach(k => {
        outStrs[k] = 1;
    });
    newOutputObjs.forEach(idObj => {
        outObjs.push(idObj);
    });
}

function checkInOutOverlap(out, inputs) {
    const {id: outId, property: outProp} = out;
    return inputs.some(in_ => {
        const {id: inId, property: inProp} = in_;
        if (outProp !== inProp || typeof outId !== typeof inId) {
            return false;
        }
        if (typeof outId === 'string') {
            if (outId === inId) {
                return true;
            }
        } else if (wildcardOverlap(in_, [out])) {
            return true;
        }
        return false;
    });
}

function findMismatchedWildcards(outputs, inputs, state, head, dispatchError) {
    const {matchKeys: out0MatchKeys} = findWildcardKeys(outputs[0].id);
    outputs.forEach((out, i) => {
        if (i && !equals(findWildcardKeys(out.id).matchKeys, out0MatchKeys)) {
            dispatchError('Mismatched `MATCH` wildcards across `Output`s', [
                head,
                `Output ${i} (${combineIdAndProp(out)})`,
                'does not have MATCH wildcards on the same keys as',
                `Output 0 (${combineIdAndProp(outputs[0])}).`,
                'MATCH wildcards must be on the same keys for all Outputs.',
                'ALL wildcards need not match, only MATCH.'
            ]);
        }
    });
    [
        [inputs, 'Input'],
        [state, 'State']
    ].forEach(([args, cls]) => {
        args.forEach((arg, i) => {
            const {matchKeys, allsmallerKeys} = findWildcardKeys(arg.id);
            const allWildcardKeys = matchKeys.concat(allsmallerKeys);
            const diff = difference(allWildcardKeys, out0MatchKeys);
            if (diff.length) {
                diff.sort();
                dispatchError('`Input` / `State` wildcards not in `Output`s', [
                    head,
                    `${cls} ${i} (${combineIdAndProp(arg)})`,
                    `has MATCH or ALLSMALLER on key(s) ${diff.join(', ')}`,
                    `where Output 0 (${combineIdAndProp(outputs[0])})`,
                    'does not have a MATCH wildcard. Inputs and State do not',
                    'need every MATCH from the Output(s), but they cannot have',
                    'extras beyond the Output(s).'
                ]);
            }
        });
    });
}

const matchWildKeys = ([a, b]) => {
    const aWild = a && a.wild;
    const bWild = b && b.wild;
    if (aWild && bWild) {
        // Every wildcard combination overlaps except MATCH<->ALLSMALLER
        return !(
            (a === MATCH && b === ALLSMALLER) ||
            (a === ALLSMALLER && b === MATCH)
        );
    }
    return a === b || aWild || bWild;
};

function wildcardOverlap({id, property}, objs) {
    const idKeys = keys(id).sort();
    const idVals = props(idKeys, id);
    for (const obj of objs) {
        const {id: id2, property: property2} = obj;
        if (
            property2 === property &&
            typeof id2 !== 'string' &&
            equals(keys(id2).sort(), idKeys) &&
            all(matchWildKeys, zip(idVals, props(idKeys, id2)))
        ) {
            return obj;
        }
    }
    return false;
}

export function validateCallbacksToLayout(state_, dispatchError) {
    const {config, graphs, layout: layout_, paths: paths_} = state_;
    const validateIds = !config.suppress_callback_exceptions;
    let layout, paths;
    if (validateIds && config.validation_layout) {
        layout = config.validation_layout;
        paths = computePaths(layout, [], null, paths_.events);
    } else {
        layout = layout_;
        paths = paths_;
    }
    const {outputMap, inputMap, outputPatterns, inputPatterns} = graphs;

    function tail(callbacks) {
        return (
            'This ID was used in the callback(s) for Output(s):\n  ' +
            callbacks
                .map(({outputs}) => outputs.map(combineIdAndProp).join(', '))
                .join('\n  ')
        );
    }

    function missingId(id, cls, callbacks) {
        dispatchError('ID not found in layout', [
            `Attempting to connect a callback ${cls} item to component:`,
            `  "${stringifyId(id)}"`,
            'but no components with that id exist in the layout.',
            '',
            'If you are assigning callbacks to components that are',
            'generated by other callbacks (and therefore not in the',
            'initial layout), you can suppress this exception by setting',
            '`suppress_callback_exceptions=True`.',
            tail(callbacks)
        ]);
    }

    function validateProp(id, idPath, rawProp, cls, callbacks) {
        const prop = rawProp.split('@')[0];
        const component = path(idPath, layout);
        const element = Registry.resolve(component);

        // note: Flow components do not have propTypes, so we can't validate.
        if (element && element.propTypes && !element.propTypes[prop]) {
            // look for wildcard props (ie data-* etc)
            for (const propName in element.propTypes) {
                const last = propName.length - 1;
                if (
                    propName.charAt(last) === '*' &&
                    prop.substr(0, last) === propName.substr(0, last)
                ) {
                    return;
                }
            }
            const {type, namespace} = component;
            dispatchError('Invalid prop for this component', [
                `Property "${prop}" was used with component ID:`,
                `  ${JSON.stringify(id)}`,
                `in one of the ${cls} items of a callback.`,
                `This ID is assigned to a ${namespace}.${type} component`,
                'in the layout, which does not support this property.',
                tail(callbacks)
            ]);
        }
    }

    function validateIdPatternProp(id, property, cls, callbacks) {
        resolveDeps()(paths)({id, property}).forEach(dep => {
            const {id: idResolved, path: idPath} = dep;
            validateProp(idResolved, idPath, property, cls, callbacks);
        });
    }

    const callbackIdsCheckedForState = {};

    function validateState(callback) {
        const {state, output} = callback;

        // ensure we don't check the same callback for state multiple times
        if (callbackIdsCheckedForState[output]) {
            return;
        }
        callbackIdsCheckedForState[output] = 1;

        const cls = 'State';

        state.forEach(({id, property}) => {
            if (typeof id === 'string') {
                const idPath = getPath(paths, id);
                if (!idPath) {
                    if (validateIds) {
                        missingId(id, cls, [callback]);
                    }
                } else {
                    validateProp(id, idPath, property, cls, [callback]);
                }
            }
            // Only validate props for State object ids that we don't need to
            // resolve them to specific inputs or outputs
            else if (!intersection([MATCH, ALLSMALLER], values(id)).length) {
                validateIdPatternProp(id, property, cls, [callback]);
            }
        });
    }

    function validateMap(map, cls, doState) {
        for (const id in map) {
            const idProps = map[id];
            const idPath = getPath(paths, id);
            if (!idPath) {
                if (validateIds) {
                    missingId(id, cls, flatten(values(idProps)));
                }
            } else {
                for (const property in idProps) {
                    const callbacks = idProps[property];
                    validateProp(id, idPath, property, cls, callbacks);
                    if (doState) {
                        // It would be redundant to check state on both inputs
                        // and outputs - so only set doState for outputs.
                        callbacks.forEach(validateState);
                    }
                }
            }
        }
    }

    validateMap(outputMap, 'Output', true);
    validateMap(inputMap, 'Input');

    function validatePatterns(patterns, cls, doState) {
        for (const keyStr in patterns) {
            const keyPatterns = patterns[keyStr];
            for (const property in keyPatterns) {
                keyPatterns[property].forEach(({keys, values, callbacks}) => {
                    const id = zipObj(keys, values);
                    validateIdPatternProp(id, property, cls, callbacks);
                    if (doState) {
                        callbacks.forEach(validateState);
                    }
                });
            }
        }
    }

    validatePatterns(outputPatterns, 'Output', true);
    validatePatterns(inputPatterns, 'Input');
}

export function computeGraphs(dependencies, dispatchError) {
    // multiGraph is just for finding circular deps
    const multiGraph = new DepGraph();

    const wildcardPlaceholders = {};

    const fixIds = map(evolve({id: parseIfWildcard}));
    const parsedDependencies = map(dep => {
        const {output} = dep;
        const out = evolve({inputs: fixIds, state: fixIds}, dep);
        out.outputs = map(
            outi => assoc('out', true, splitIdAndProp(outi)),
            isMultiOutputProp(output) ? parseMultipleOutputs(output) : [output]
        );
        return out;
    }, dependencies);

    let hasError = false;
    const wrappedDE = (message, lines) => {
        hasError = true;
        dispatchError(message, lines);
    };
    validateDependencies(parsedDependencies, wrappedDE);

    /*
     * For regular ids, outputMap and inputMap are:
     *   {[id]: {[prop]: [callback, ...]}}
     * where callbacks are the matching specs from the original
     * dependenciesRequest, but with outputs parsed to look like inputs,
     * and a list matchKeys added if the outputs have MATCH wildcards.
     * For outputMap there should only ever be one callback per id/prop
     * but for inputMap there may be many.
     *
     * For wildcard ids, outputPatterns and inputPatterns are:
     *   {
     *       [keystr]: {
     *           [prop]: [
     *               {keys: [...], values: [...], callbacks: [callback, ...]},
     *               {...}
     *           ]
     *       }
     *   }
     * keystr is a stringified ordered list of keys in the id
     * keys is the same ordered list (just copied for convenience)
     * values is an array of explicit or wildcard values for each key in keys
     */
    const outputMap = {};
    const inputMap = {};
    const outputPatterns = {};
    const inputPatterns = {};

    const finalGraphs = {
        MultiGraph: multiGraph,
        outputMap,
        inputMap,
        outputPatterns,
        inputPatterns,
        callbacks: parsedDependencies
    };

    if (hasError) {
        // leave the graphs empty if we found an error, so we don't try to
        // execute the broken callbacks.
        return finalGraphs;
    }

    parsedDependencies.forEach(dependency => {
        const {outputs, inputs} = dependency;

        outputs.concat(inputs).forEach(item => {
            const {id} = item;
            if (typeof id === 'object') {
                forEachObjIndexed((val, key) => {
                    if (!wildcardPlaceholders[key]) {
                        wildcardPlaceholders[key] = {
                            exact: [],
                            expand: 0
                        };
                    }
                    const keyPlaceholders = wildcardPlaceholders[key];
                    if (val && val.wild) {
                        if (val.expand) {
                            keyPlaceholders.expand += 1;
                        }
                    } else if (keyPlaceholders.exact.indexOf(val) === -1) {
                        keyPlaceholders.exact.push(val);
                    }
                }, id);
            }
        });
    });

    forEachObjIndexed(keyPlaceholders => {
        const {exact, expand} = keyPlaceholders;
        const vals = exact.slice().sort(idValSort);
        if (expand) {
            for (let i = 0; i < expand; i++) {
                if (exact.length) {
                    vals.splice(0, 0, [valBefore(vals[0])]);
                    vals.push(valAfter(vals[vals.length - 1]));
                } else {
                    vals.push(i);
                }
            }
        } else if (!exact.length) {
            // only MATCH/ALL - still need a value
            vals.push(0);
        }
        keyPlaceholders.vals = vals;
    }, wildcardPlaceholders);

    function makeAllIds(idSpec, outIdFinal) {
        let idList = [{}];
        forEachObjIndexed((val, key) => {
            const testVals = wildcardPlaceholders[key].vals;
            const outValIndex = testVals.indexOf(outIdFinal[key]);
            let newVals = [val];
            if (val && val.wild) {
                if (val === ALLSMALLER) {
                    if (outValIndex > 0) {
                        newVals = testVals.slice(0, outValIndex);
                    } else {
                        // no smaller items - delete all outputs.
                        newVals = [];
                    }
                } else {
                    // MATCH or ALL
                    // MATCH *is* ALL for outputs, ie we don't already have a
                    // value specified in `outIdFinal`
                    newVals =
                        outValIndex === -1 || val === ALL
                            ? testVals
                            : [outIdFinal[key]];
                }
            }
            // replicates everything in idList once for each item in
            // newVals, attaching each value at key.
            idList = ap(ap([assoc(key)], newVals), idList);
        }, idSpec);
        return idList;
    }

    /* multiGraph is used only for testing circularity
     *
     * Each component+property that is used as an input or output is added as a node
     * to a directed graph with a dependency from each input to each output. The
     * function triggerDefaultState in index.js then checks this graph for circularity.
     *
     * In order to allow the same component+property to be both an input and output
     * of the same callback, a two pass approach is used.
     *
     * In the first pass, the graph is built up normally with the exception that
     * in cases where an output is also an input to the same callback a special
     * "output" node is added and the dependencies target this output node instead.
     * For example, if `slider.value` is both an input and an output, then the a new
     * node `slider.value__output` will be added with a dependency from `slider.value`
     * to `slider.value__output`. Splitting the input and output into separate nodes
     * removes the circularity.
     *
     * In order to still detect other forms of circularity, it is necessary to do a
     * second pass and add the new output nodes as a dependency in any *other* callbacks
     * where the original node was an input. Continuing the example, any other callback
     * that had `slider.value` as an input dependency also needs to have
     * `slider.value__output` as a dependency. To make this efficient, all the inputs
     * and outputs for each callback are stored during the first pass.
     */

    const outputTag = '__output';
    const duplicateOutputs = [];
    const cbIn = [];
    const cbOut = [];

    function addInputToMulti(inIdProp, outIdProp, firstPass = true) {
        multiGraph.addNode(inIdProp);
        multiGraph.addDependency(inIdProp, outIdProp);
        // only store callback inputs and outputs during the first pass
        if (firstPass) {
            cbIn[cbIn.length - 1].push(inIdProp);
            cbOut[cbOut.length - 1].push(outIdProp);
        }
    }

    parsedDependencies.forEach(dependency => {
        const {outputs, inputs} = dependency;

        // new callback, add an empty array for its inputs and outputs
        cbIn.push([]);
        cbOut.push([]);

        function addOutputToMulti(outIdFinal, outIdProp) {
            multiGraph.addNode(outIdProp);
            inputs.forEach(inObj => {
                const {id: inId, property} = inObj;
                if (typeof inId === 'object') {
                    const inIdList = makeAllIds(inId, outIdFinal);
                    inIdList.forEach(id => {
                        addInputToMulti(
                            combineIdAndProp({id, property}),
                            outIdProp
                        );
                    });
                } else {
                    addInputToMulti(combineIdAndProp(inObj), outIdProp);
                }
            });
        }

        // We'll continue to use dep.output as its id, but add outputs as well
        // for convenience and symmetry with the structure of inputs and state.
        // Also collect MATCH keys in the output (all outputs must share these)
        // and ALL keys in the first output (need not be shared but we'll use
        // the first output for calculations) for later convenience.
        const {matchKeys} = findWildcardKeys(outputs[0].id);
        const firstSingleOutput = findIndex(o => !isMultiValued(o.id), outputs);
        const finalDependency = mergeRight(
            {matchKeys, firstSingleOutput, outputs},
            dependency
        );

        outputs.forEach(outIdProp => {
            const {id: outId, property} = outIdProp;
            // check if this output is also an input to the same callback
            const alsoInput = checkInOutOverlap(outIdProp, inputs);
            if (typeof outId === 'object') {
                const outIdList = makeAllIds(outId, {});
                outIdList.forEach(id => {
                    const tempOutIdProp = {id, property};
                    let outIdName = combineIdAndProp(tempOutIdProp);
                    // if this output is also an input, add `outputTag` to the name
                    if (alsoInput) {
                        duplicateOutputs.push(tempOutIdProp);
                        outIdName += outputTag;
                    }
                    addOutputToMulti(id, outIdName);
                });
                addPattern(outputPatterns, outId, property, finalDependency);
            } else {
                let outIdName = combineIdAndProp(outIdProp);
                // if this output is also an input, add `outputTag` to the name
                if (alsoInput) {
                    duplicateOutputs.push(outIdProp);
                    outIdName += outputTag;
                }
                addOutputToMulti({}, outIdName);
                addMap(outputMap, outId, property, finalDependency);
            }
        });

        inputs.forEach(inputObject => {
            const {id: inId, property: inProp} = inputObject;
            if (typeof inId === 'object') {
                addPattern(inputPatterns, inId, inProp, finalDependency);
            } else {
                addMap(inputMap, inId, inProp, finalDependency);
            }
        });
    });

    // second pass for adding new output nodes as dependencies where needed
    duplicateOutputs.forEach(dupeOutIdProp => {
        const originalName = combineIdAndProp(dupeOutIdProp);
        const newName = originalName.concat(outputTag);
        for (var cnt = 0; cnt < cbIn.length; cnt++) {
            // check if input to the callback
            if (cbIn[cnt].some(inName => inName === originalName)) {
                /* make sure it's not also an output of the callback
                 * (this will be the original callback)
                 */
                if (!cbOut[cnt].some(outName => outName === newName)) {
                    cbOut[cnt].forEach(outName => {
                        addInputToMulti(newName, outName, false);
                    });
                }
            }
        }
    });

    return finalGraphs;
}

function findWildcardKeys(id) {
    const matchKeys = [];
    const allsmallerKeys = [];
    if (typeof id === 'object') {
        forEachObjIndexed((val, key) => {
            if (val === MATCH) {
                matchKeys.push(key);
            } else if (val === ALLSMALLER) {
                allsmallerKeys.push(key);
            }
        }, id);
        matchKeys.sort();
        allsmallerKeys.sort();
    }
    return {matchKeys, allsmallerKeys};
}

/*
 * Do the given id values `vals` match the pattern `patternVals`?
 * `keys`, `patternVals`, and `vals` are all arrays, and we already know that
 * we're only looking at ids with the same keys as the pattern.
 *
 * Optionally, include another reference set of the same - to ensure the
 * correct matching of MATCH or ALLSMALLER between input and output items.
 */
export function idMatch(
    keys,
    vals,
    patternVals,
    refKeys,
    refVals,
    refPatternVals
) {
    for (let i = 0; i < keys.length; i++) {
        const val = vals[i];
        const patternVal = patternVals[i];
        if (patternVal.wild) {
            // If we have a second id, compare the wildcard values.
            // Without a second id, all wildcards pass at this stage.
            if (refKeys && patternVal !== ALL) {
                const refIndex = refKeys.indexOf(keys[i]);
                const refPatternVal = refPatternVals[refIndex];
                // Sanity check. Shouldn't ever fail this, if the back end
                // did its job validating callbacks.
                // You can't resolve an input against an input, because
                // two ALLSMALLER's wouldn't make sense!
                if (patternVal === ALLSMALLER && refPatternVal === ALLSMALLER) {
                    throw new Error(
                        'invalid wildcard id pair: ' +
                            JSON.stringify({
                                keys,
                                patternVals,
                                vals,
                                refKeys,
                                refPatternVals,
                                refVals
                            })
                    );
                }
                if (
                    idValSort(val, refVals[refIndex]) !==
                    (patternVal === ALLSMALLER
                        ? -1
                        : refPatternVal === ALLSMALLER
                        ? 1
                        : 0)
                ) {
                    return false;
                }
            }
        } else if (val !== patternVal) {
            return false;
        }
    }
    return true;
}

function getAnyVals(patternVals, vals) {
    const matches = [];
    for (let i = 0; i < patternVals.length; i++) {
        if (patternVals[i] === MATCH) {
            matches.push(vals[i]);
        }
    }
    return matches.length ? JSON.stringify(matches) : '';
}

/*
 * Does this item (input / output / state) support multiple values?
 * string IDs do not; wildcard IDs only do if they contain ALL or ALLSMALLER
 */
export function isMultiValued({id}) {
    return typeof id === 'object' && any(v => v.multi, values(id));
}

/*
 * For a given output id and prop, find the callback generating it.
 * If no callback is found, returns false.
 * If one is found, returns:
 * {
 *     callback: the callback spec {outputs, inputs, state etc}
 *     anyVals: stringified list of resolved MATCH keys we matched
 *     resolvedId: the "outputs" id string plus MATCH values we matched
 *     getOutputs: accessor function to give all resolved outputs of this
 *         callback. Takes `paths` as argument to apply when the callback is
 *         dispatched, in case a previous callback has altered the layout.
 *         The result is a list of {id (string or object), property (string)}
 *     getInputs: same for inputs
 *     getState: same for state
 *     changedPropIds: an object of {[idAndProp]: v} triggering this callback
 *         v = DIRECT (2): the prop was changed in the front end, so dependent
 *             callbacks *MUST* be executed.
 *         v = INDIRECT (1): the prop is expected to be changed by a callback,
 *             but if this is prevented, dependent callbacks may be pruned.
 *     initialCall: boolean, if true we don't require any changedPropIds
 *         to keep this callback around, as it's the initial call to populate
 *         this value on page load or changing part of the layout.
 *         By default this is true for callbacks generated by
 *         getCallbackByOutput, false from getCallbacksByInput.
 * }
 */
function getCallbackByOutput(graphs, paths, id, prop) {
    let resolve;
    let callback;
    let anyVals = '';
    if (typeof id === 'string') {
        // standard id version
        const callbacks = (graphs.outputMap[id] || {})[prop];
        if (callbacks) {
            callback = callbacks[0];
            resolve = resolveDeps();
        }
    } else {
        // wildcard version
        const keys = Object.keys(id).sort();
        const vals = props(keys, id);
        const keyStr = keys.join(',');
        const patterns = (graphs.outputPatterns[keyStr] || {})[prop];
        if (patterns) {
            for (let i = 0; i < patterns.length; i++) {
                const patternVals = patterns[i].values;
                if (idMatch(keys, vals, patternVals)) {
                    callback = patterns[i].callbacks[0];
                    resolve = resolveDeps(keys, vals, patternVals);
                    anyVals = getAnyVals(patternVals, vals);
                    break;
                }
            }
        }
    }
    if (!resolve) {
        return false;
    }

    return makeResolvedCallback(callback, resolve, anyVals);
}

function addResolvedFromOutputs(callback, outPattern, outs, matches) {
    const out0Keys = Object.keys(outPattern.id).sort();
    const out0PatternVals = props(out0Keys, outPattern.id);
    const foundCbIds = {};
    outs.forEach(({id: outId}) => {
        const outVals = props(out0Keys, outId);
        const resolved = makeResolvedCallback(
            callback,
            resolveDeps(out0Keys, outVals, out0PatternVals),
            getAnyVals(out0PatternVals, outVals)
        );
        const {resolvedId} = resolved;
        if (!foundCbIds[resolvedId]) {
            matches.push(resolved);
            foundCbIds[resolvedId] = true;
        }
    });
}

export function addAllResolvedFromOutputs(resolve, paths, matches) {
    return callback => {
        const {matchKeys, firstSingleOutput, outputs} = callback;
        if (matchKeys.length) {
            const singleOutPattern = outputs[firstSingleOutput];
            if (singleOutPattern) {
                addResolvedFromOutputs(
                    callback,
                    singleOutPattern,
                    resolve(paths)(singleOutPattern),
                    matches
                );
            } else {
                /*
                 * If every output has ALL we need to reduce resolved set
                 * to one item per combination of MATCH values.
                 * That will give one result per callback invocation.
                 */
                const anySeen = {};
                outputs.forEach(outPattern => {
                    const outSet = resolve(paths)(outPattern).filter(i => {
                        const matchStr = JSON.stringify(props(matchKeys, i.id));
                        if (!anySeen[matchStr]) {
                            anySeen[matchStr] = 1;
                            return true;
                        }
                        return false;
                    });
                    addResolvedFromOutputs(
                        callback,
                        outPattern,
                        outSet,
                        matches
                    );
                });
            }
        } else {
            const cb = makeResolvedCallback(callback, resolve, '');
            if (flatten(cb.getOutputs(paths)).length) {
                matches.push(cb);
            }
        }
    };
}

/*
 * For a given id and prop find all callbacks it's an input of.
 *
 * Returns an array of objects:
 *   {callback, resolvedId, getOutputs, getInputs, getState}
 *   See getCallbackByOutput for details.
 *
 * Note that if the original input contains an ALLSMALLER wildcard,
 * there may be many entries for the same callback, but any given output
 * (with an MATCH corresponding to the input's ALLSMALLER) will only appear
 * in one entry.
 */
export function getWatchedKeys(id, newProps, graphs) {
    if (!(id && graphs && newProps.length)) {
        return [];
    }

    if (typeof id === 'string') {
        const inputs = graphs.inputMap[id];
        return inputs ? newProps.filter(newProp => inputs[newProp]) : [];
    }

    const keys = Object.keys(id).sort();
    const vals = props(keys, id);
    const keyStr = keys.join(',');
    const keyPatterns = graphs.inputPatterns[keyStr];
    if (!keyPatterns) {
        return [];
    }
    return newProps.filter(prop => {
        const patterns = keyPatterns[prop];
        return (
            patterns &&
            patterns.some(pattern => idMatch(keys, vals, pattern.values))
        );
    });
}

/*
 * Return a list of all callbacks referencing a chunk of the layout,
 * either as inputs or outputs.
 *
 * opts.outputsOnly: boolean, set true when crawling the *whole* layout,
 *   because outputs are enough to get everything.
 * opts.removedArrayInputsOnly: boolean, set true to only look for inputs in
 *   wildcard arrays (ALL or ALLSMALLER), no outputs. This gets used to tell
 *   when the new *absence* of a given component should trigger a callback.
 * opts.newPaths: paths object after the edit - to be used with
 *   removedArrayInputsOnly to determine if the callback still has its outputs
 * opts.chunkPath: path to the new chunk - used to determine if any outputs are
 *   outside of this chunk, because this determines whether inputs inside the
 *   chunk count as having changed
 *
 * Returns an array of objects:
 *   {callback, resolvedId, getOutputs, getInputs, getState, ...etc}
 *   See getCallbackByOutput for details.
 */
export function getUnfilteredLayoutCallbacks(graphs, paths, layoutChunk, opts) {
    const {outputsOnly, removedArrayInputsOnly, newPaths, chunkPath} = opts;
    const foundCbIds = {};
    const callbacks = [];

    function addCallback(callback) {
        if (callback) {
            const foundIndex = foundCbIds[callback.resolvedId];
            if (foundIndex !== undefined) {
                const foundCb = callbacks[foundIndex];
                foundCb.changedPropIds = mergeMax(
                    foundCb.changedPropIds,
                    callback.changedPropIds
                );
                if (callback.initialCall) {
                    foundCb.initialCall = true;
                }
            } else {
                foundCbIds[callback.resolvedId] = callbacks.length;
                callbacks.push(callback);
            }
        }
    }

    function addCallbackIfArray(idStr) {
        return cb =>
            cb.getInputs(paths).some(ini => {
                if (
                    Array.isArray(ini) &&
                    ini.some(inij => stringifyId(inij.id) === idStr)
                ) {
                    // This callback should trigger even with no changedProps,
                    // since the props that changed no longer exist.
                    // We're kind of abusing the `initialCall` flag here, it's
                    // more like a "final call" for the removed inputs, but
                    // this case is not subject to `prevent_initial_call`.
                    if (flatten(cb.getOutputs(newPaths)).length) {
                        cb.initialCall = true;
                        cb.changedPropIds = {};
                        addCallback(cb);
                    }
                    return true;
                }
                return false;
            });
    }

    function handleOneId(id, outIdCallbacks, inIdCallbacks) {
        if (outIdCallbacks) {
            for (const property in outIdCallbacks) {
                const cb = getCallbackByOutput(graphs, paths, id, property);
                if (cb) {
                    // callbacks found in the layout by output should always run
                    // unless specifically requested not to.
                    // ie this is the initial call of this callback even if it's
                    // not the page initialization but just a new layout chunk
                    if (!cb.callback.prevent_initial_call) {
                        cb.initialCall = true;
                        addCallback(cb);
                    }
                }
            }
        }
        if (!outputsOnly && inIdCallbacks) {
            const maybeAddCallback = removedArrayInputsOnly
                ? addCallbackIfArray(stringifyId(id))
                : addCallback;
            let handleThisCallback = maybeAddCallback;
            if (chunkPath) {
                handleThisCallback = cb => {
                    if (
                        !all(
                            startsWith(chunkPath),
                            pluck('path', flatten(cb.getOutputs(paths)))
                        )
                    ) {
                        maybeAddCallback(cb);
                    }
                };
            }
            for (const property in inIdCallbacks) {
                getCallbacksByInput(
                    graphs,
                    paths,
                    id,
                    property,
                    INDIRECT
                ).forEach(handleThisCallback);
            }
        }
    }

    crawlLayout(layoutChunk, child => {
        const id = path(['props', 'id'], child);
        if (id) {
            if (typeof id === 'string' && !removedArrayInputsOnly) {
                handleOneId(id, graphs.outputMap[id], graphs.inputMap[id]);
            } else {
                const keyStr = Object.keys(id).sort().join(',');
                handleOneId(
                    id,
                    !removedArrayInputsOnly && graphs.outputPatterns[keyStr],
                    graphs.inputPatterns[keyStr]
                );
            }
        }
    });

    return map(
        cb => ({
            ...cb,
            priority: getPriority(graphs, paths, cb)
        }),
        callbacks
    );
}
