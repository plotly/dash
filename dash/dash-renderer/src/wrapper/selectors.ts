import {DashLayoutPath, DashComponent, BaseDashProps} from '../types/component';
import {getComponentLayout, stringifyPath} from './wrapping';

type SelectDashProps = [DashComponent, BaseDashProps, number];

export const selectDashProps =
    (componentPath: DashLayoutPath) =>
    (state: any): SelectDashProps => {
        const c = getComponentLayout(componentPath, state);
        // Layout hashes records the number of times a path has been updated.
        // sum with the parents hash (match without the last ']') to get the real hash
        // Then it can be easily compared without having to compare the props.
        const strPath = stringifyPath(componentPath);

        const h = Object.entries(state.layoutHashes).reduce(
            (acc, [updatedPath, pathHash]) =>
                strPath.startsWith(updatedPath)
                    ? (pathHash as number) + acc
                    : acc,
            0
        );
        return [c, c.props, h];
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
