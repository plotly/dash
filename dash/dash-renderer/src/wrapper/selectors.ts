import {path} from 'ramda';

import {DashLayoutPath, DashComponent, BaseDashProps} from '../types/component';

type SelectDashProps = [DashComponent, BaseDashProps, number];

export const selectDashProps =
    (componentPath: DashLayoutPath) =>
    (state: any): SelectDashProps => {
        const c = path(componentPath, state.layout) as DashComponent;
        // Layout hashes records the number of times a path has been updated.
        // sum with the parents hash (match without the last ']') to get the real hash
        // Then it can be easily compared without having to compare the props.
        let jsonPath = JSON.stringify(componentPath);
        jsonPath = jsonPath.substring(0, jsonPath.length - 1);

        const h = Object.entries(state.layoutHashes).reduce(
            (acc, [path, pathHash]) =>
                jsonPath.startsWith(path.substring(0, path.length - 1))
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
