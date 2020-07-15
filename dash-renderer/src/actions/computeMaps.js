import isNumeric from 'fast-isnumeric';

import {
    all,
    difference,
    equals,
    evolve,
    findIndex,
    forEachObjIndexed,
    includes,
    isEmpty,
    keys,
    map,
    mergeRight,
    props,
    zip,
} from 'ramda';

import {
    ALLSMALLER,
    MATCH,
    allowedWildcards,
    idValSort,
    isMultiValued,
} from './dependencies';
import {combineIdAndProp, parseIfWildcard} from './dependencies_ts';

/*
 * Provide a value known to be before or after v, according to idValSort
 */
const valBefore = v => (isNumeric(v) ? v - 1 : 0);
const valAfter = v => (typeof v === 'string' ? v + 'z' : 'z');

export default callbackDefinitions => {
    const wildcardPlaceholders = {};

    const fixIds = map(evolve({id: parseIfWildcard}));
    const parsedDependencies = map(dep => {
        const out = evolve(
            {inputs: fixIds, outputs: fixIds, state: fixIds},
            dep
        );
        return out;
    }, callbackDefinitions);

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
        outputMap,
        inputMap,
        outputPatterns,
        inputPatterns,
        callbacks: parsedDependencies,
    };

    parsedDependencies.forEach(dependency => {
        const {outputs, inputs} = dependency;

        outputs.concat(inputs).forEach(item => {
            const {id} = item;
            if (typeof id === 'object') {
                forEachObjIndexed((val, key) => {
                    wildcardPlaceholders[key] = wildcardPlaceholders[key] ?? {
                        exact: [],
                        expand: 0,
                    };

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
                    vals.unshift(valBefore(vals[0]));
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

    parsedDependencies.forEach(function registerDependency(dependency) {
        const {outputs, inputs} = dependency;

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
            if (typeof outId === 'object') {
                addPattern(outputPatterns, outId, property, finalDependency);
            } else {
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

    return finalGraphs;
};

const idInvalidChars = ['.', '{'];

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

const wildcardValTypes = ['string', 'number', 'boolean'];

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

function findDuplicateOutputs(outputs, head, dispatchError, outStrs, outObjs) {
    const newOutputStrs = {};
    const newOutputObjs = [];
    outputs.forEach(({id, mutation, property}, i) => {
        // Callback outputs involving mutations don't count against duplicated outputs
        if (mutation) {
            return;
        }

        if (typeof id === 'string') {
            const idProp = combineIdAndProp({id, property});
            if (newOutputStrs[idProp]) {
                dispatchError('Duplicate callback Outputs', [
                    head,
                    `Output ${i} (${idProp}) is already used by this callback.`,
                ]);
            } else if (outStrs[idProp]) {
                dispatchError('Duplicate callback outputs', [
                    head,
                    `Output ${i} (${idProp}) is already in use.`,
                    'Any given output can only have one callback that sets it.',
                    'To resolve this situation, try combining these into',
                    'one callback function, distinguishing the trigger',
                    'by using `dash.callback_context` if necessary.',
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
                    `used in ${selfOverlap ? 'this' : 'a different'} callback.`,
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

function findInOutOverlap(outputs, inputs, head, dispatchError) {
    outputs.forEach((out, outi) => {
        const {id: outId, property: outProp} = out;
        inputs.forEach((in_, ini) => {
            const {id: inId, property: inProp} = in_;
            if (outProp !== inProp || typeof outId !== typeof inId) {
                return;
            }
            if (typeof outId === 'string') {
                if (outId === inId) {
                    dispatchError('Same `Input` and `Output`', [
                        head,
                        `Input ${ini} (${combineIdAndProp(in_)})`,
                        `matches Output ${outi} (${combineIdAndProp(out)})`,
                    ]);
                }
            } else if (wildcardOverlap(in_, [out])) {
                dispatchError('Same `Input` and `Output`', [
                    head,
                    `Input ${ini} (${combineIdAndProp(in_)})`,
                    'can match the same component(s) as',
                    `Output ${outi} (${combineIdAndProp(out)})`,
                ]);
            }
        });
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
                'ALL wildcards need not match, only MATCH.',
            ]);
        }
    });
    [
        [inputs, 'Input'],
        [state, 'State'],
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
                    'extras beyond the Output(s).',
                ]);
            }
        });
    });
}

function validateArg({id, property}, head, cls, i, dispatchError) {
    if (typeof property !== 'string' || !property) {
        dispatchError('Callback property error', [
            head,
            `${cls}[${i}].property = ${JSON.stringify(property)}`,
            'but we expected `property` to be a non-empty string.',
        ]);
    }

    if (typeof id === 'object') {
        if (isEmpty(id)) {
            dispatchError('Callback item missing ID', [
                head,
                `${cls}[${i}].id = {}`,
                'Every item linked to a callback needs an ID',
            ]);
        }

        forEachObjIndexed((v, k) => {
            if (!k) {
                dispatchError('Callback wildcard ID error', [
                    head,
                    `${cls}[${i}].id has key "${k}"`,
                    'Keys must be non-empty strings.',
                ]);
            }

            if (typeof v === 'object' && v.wild) {
                if (allowedWildcards[cls][v.wild] !== v) {
                    dispatchError('Callback wildcard ID error', [
                        head,
                        `${cls}[${i}].id["${k}"] = ${v.wild}`,
                        `Allowed wildcards for ${cls}s are:`,
                        keys(allowedWildcards[cls]).join(', '),
                    ]);
                }
            } else if (!includes(typeof v, wildcardValTypes)) {
                dispatchError('Callback wildcard ID error', [
                    head,
                    `${cls}[${i}].id["${k}"] = ${JSON.stringify(v)}`,
                    'Wildcard callback ID values must be either wildcards',
                    'or constants of one of these types:',
                    wildcardValTypes.join(', '),
                ]);
            }
        }, id);
    } else if (typeof id === 'string') {
        if (!id) {
            dispatchError('Callback item missing ID', [
                head,
                `${cls}[${i}].id = "${id}"`,
                'Every item linked to a callback needs an ID',
            ]);
        }
        const invalidChars = idInvalidChars.filter(c => includes(c, id));
        if (invalidChars.length) {
            dispatchError('Callback invalid ID string', [
                head,
                `${cls}[${i}].id = '${id}'`,
                `characters '${invalidChars.join("', '")}' are not allowed.`,
            ]);
        }
    } else {
        dispatchError('Callback ID type error', [
            head,
            `${cls}[${i}].id = ${JSON.stringify(id)}`,
            'IDs must be strings or wildcard-compatible objects.',
        ]);
    }
}

export function validateDependencies(parsedDependencies, dispatchError) {
    let valid = true;
    const _dispatchError = (message, lines) => {
        valid = false;
        dispatchError(message, lines);
    };

    const outStrs = {};
    const outObjs = [];

    parsedDependencies.forEach(dep => {
        const {inputs, outputs, state} = dep;
        let hasOutputs = true;
        if (outputs.length === 1 && !outputs[0].id && !outputs[0].property) {
            hasOutputs = false;
            _dispatchError('A callback is missing Outputs', [
                'Please provide an output for this callback:',
                JSON.stringify(dep, null, 2),
            ]);
        }

        const head =
            'In the callback for output(s):\n  ' +
            outputs.map(combineIdAndProp).join('\n  ');

        if (!inputs.length) {
            _dispatchError('A callback is missing Inputs', [
                head,
                'there are no `Input` elements.',
                'Without `Input` elements, it will never get called.',
                '',
                'Subscribing to `Input` components will cause the',
                'callback to be called whenever their values change.',
            ]);
        }

        const spec = [
            [outputs, 'Output'],
            [inputs, 'Input'],
            [state, 'State'],
        ];
        spec.forEach(([args, cls]) => {
            if (cls === 'Output' && !hasOutputs) {
                // just a quirk of how we pass & parse outputs - if you don't
                // provide one, it looks like a single blank output. This is
                // actually useful for graceful failure, so we work around it.
                return;
            }

            if (!Array.isArray(args)) {
                _dispatchError(`Callback ${cls}(s) must be an Array`, [
                    head,
                    `For ${cls}(s) we found:`,
                    JSON.stringify(args),
                    'but we expected an Array.',
                ]);
            }
            args.forEach((idProp, i) => {
                validateArg(idProp, head, cls, i, dispatchError);
            });
        });

        findDuplicateOutputs(outputs, head, dispatchError, outStrs, outObjs);
        findInOutOverlap(outputs, inputs, head, dispatchError);
        findMismatchedWildcards(outputs, inputs, state, head, dispatchError);
    });

    return valid;
}

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
