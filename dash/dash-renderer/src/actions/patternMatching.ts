import {keys, equals, dissoc, toPairs} from 'ramda';
import {ICallbackPayload} from '../types/callbacks';

/**
 * Deserialize pattern matching ids that come in one of the form:
 * - '{"type":"component","index":["MATCH"]}.children'
 * - '{"type":"component","index":["MATCH"]}'
 *
 * @param id The raw object as a string id.
 * @returns The id object.
 */
export function parsePMCId(id: string): [any, string | undefined] {
    let componentId, propName;
    const index = id.lastIndexOf('}');
    if (index + 2 < id.length) {
        propName = id.substring(index + 2);
        componentId = JSON.parse(id.substring(0, index + 1));
    } else {
        componentId = JSON.parse(id);
    }
    return [componentId, propName];
}

/**
 * Get all the associated ids for an id.
 *
 * @param id Id to get all the pmc ids from.
 * @param state State of the store.
 * @param triggerKey Key to remove from the equality comparison.
 * @returns
 */
export function getAllPMCIds(id: any, state: any, triggerKey: string) {
    const keysOfIds = keys(id);
    const idKey = keysOfIds.join(',');
    return state.paths.objs[idKey]
        .map((obj: any) =>
            keysOfIds.reduce((acc, key, i) => {
                acc[key] = obj.values[i];
                return acc;
            }, {} as any)
        )
        .filter((obj: any) =>
            equals(dissoc(triggerKey, obj), dissoc(triggerKey, id))
        );
}

/**
 * Replace the pattern matching ids with the actual trigger value
 * for MATCH, all the ids for ALL and smaller than the trigger value
 * for ALLSMALLER.
 *
 * @param id The parsed id in dictionary format.
 * @param cb Original callback info.
 * @param index Index of the dependency in case there is more than one changed id.
 * @param getState Function to get the state of the redux store.
 * @returns List of replaced ids.
 */
export function replacePMC(
    id: any,
    cb: ICallbackPayload,
    index: number,
    getState: any
): any[] {
    let extras: any = [];
    const replaced: any = {};
    toPairs(id).forEach(([key, value]) => {
        if (extras.length) {
            // All done.
            return;
        }
        if (Array.isArray(value)) {
            const triggerValue = (cb.parsedChangedPropsIds[index] ||
                cb.parsedChangedPropsIds[0])[key];
            if (value.includes('MATCH')) {
                replaced[key] = triggerValue;
            } else if (value.includes('ALL')) {
                extras = getAllPMCIds(id, getState(), key);
            } else if (value.includes('ALLSMALLER')) {
                extras = getAllPMCIds(id, getState(), key).filter(
                    (obj: any) => obj[key] < triggerValue
                );
            }
        } else {
            replaced[key] = value;
        }
    });
    if (extras.length) {
        return extras;
    }
    return [replaced];
}
