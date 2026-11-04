import {DashLayoutPath, DashComponent, BaseDashProps} from '../types/component';
import {
    getComponentLayout,
    stringifyPath,
    checkDashChildrenUpdate
} from './wrapping';
import {pathOr} from 'ramda';

type SelectDashProps = [DashComponent, BaseDashProps, number, object, string];

interface ChangedPropsRecord {
    hash: number;
    changedProps: Record<string, any>;
    renderType: string;
}

interface Hashes {
    [key: string]: any; // Index signature for string keys with number values
}

const previousHashes: Hashes = {};

const NOT_FIRST_LEVEL_CHILD: [boolean, string[]] = [false, []];

const isFirstLevelPropsChild = (
    updatedPath: string,
    strPath: string
): [boolean, string[]] => {
    // This runs for every layoutHashes entry and most are unrelated, so reject
    // them before splitting. strPath must end on a segment boundary.
    if (
        !updatedPath.startsWith(strPath) ||
        (updatedPath.length > strPath.length &&
            updatedPath[strPath.length] !== ',')
    ) {
        return NOT_FIRST_LEVEL_CHILD;
    }

    // Get the remaining path after the prefix
    const remainingSegments = updatedPath.slice(strPath.length + 1).split(',');

    const propsCount = remainingSegments.filter(s => s === 'props').length;

    return [propsCount < 2, remainingSegments];
};

function determineChangedProps(
    state: any,
    strPath: string
): ChangedPropsRecord {
    let combinedHash = 0;
    let renderType: any; // Default render type, adjust as needed
    const changedProps: Record<string, any> = {};
    Object.keys(state.layoutHashes).forEach(updatedPath => {
        const [descendant, remainingSegments] = isFirstLevelPropsChild(
            updatedPath,
            strPath
        );
        if (descendant) {
            const pathHash = state.layoutHashes[updatedPath];
            const previousHash: any = pathOr({}, [updatedPath], previousHashes);
            combinedHash += pathOr(0, ['hash'], pathHash);
            if (previousHash !== pathHash) {
                if (updatedPath !== strPath) {
                    Object.assign(changedProps, {[remainingSegments[1]]: true});
                    renderType = 'components';
                } else {
                    Object.assign(
                        changedProps,
                        pathOr({}, ['changedProps'], pathHash)
                    );
                    renderType = pathOr({}, ['renderType'], pathHash);
                }
                previousHashes[updatedPath] = pathHash;
            }
        }
    });

    return {
        hash: combinedHash,
        changedProps,
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
        if (checkDashChildrenUpdate(c)) {
            hash = determineChangedProps(state, strPath);
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
