import {DashLayoutPath, DashComponent, BaseDashProps} from '../types/component';
import {getComponentLayout, stringifyPath, checkChildrenLayoutHashes} from './wrapping';
import {pathOr} from 'ramda'

type SelectDashProps = [DashComponent, BaseDashProps, number, object, string];

interface ChangedPropsRecord {
    hash: number;
    changedProps: Record<string, any>;
    renderType: string;
}

const previousHashes = {}

function determineChangedProps(state: any, strPath: string): ChangedPropsRecord {
    let combinedHash = 0;
    let renderType = 'update'; // Default render type, adjust as needed
    Object.entries(state.layoutHashes).forEach(([updatedPath, pathHash]) => {
        if (updatedPath.startsWith(strPath)) {
            const previousHash: any = pathOr({}, [updatedPath], previousHashes);
            combinedHash += pathOr(0, ['hash'], pathHash)
            if (previousHash !== pathHash) {
                previousHash[updatedPath] = pathHash
            }
        }
    });

    return {
        hash: combinedHash,
        changedProps: {},
        renderType
    };
}

export const selectDashProps =
    (componentPath: DashLayoutPath) =>
    (state: any): SelectDashProps => {
        const c = getComponentLayout(componentPath, state);
        // Layout hashes records the number of times a path has been updated.
        // sum with the parents hash (match without the last ']') to get the real hash
        // Then it can be easily compared without having to compare the props.
        const strPath = stringifyPath(componentPath);

        let hash;
        if (checkChildrenLayoutHashes(c)) {
            hash = determineChangedProps(state, strPath)
        } else {
            hash = state.layoutHashes[strPath];
        }
        let h = 0;
        let changedProps: object = {};
        let renderType = '';
        if (hash) {
            h = hash['hash'];
            changedProps = hash['changedProps'];
            renderType = hash['renderType'];
        }
        return [c, c?.props, h, changedProps, renderType];
    };

export function selectDashPropsEqualityFn(
    [_, __, hash]: SelectDashProps,
    [___, ____, previousHash]: SelectDashProps
) {
    // Only need to compare the hash as any change is summed up
    return hash === previousHash;
}

export function selectConfig(state: any) {
    return state.config;
}
