import {path} from 'ramda';

import {DashLayoutPath, DashComponent, BaseDashProps} from '../types/component';

type SelectDashProps = [DashComponent, BaseDashProps];

export const selectDashProps =
    (componentPath: DashLayoutPath) =>
    (state: any): SelectDashProps => {
        const c = path(componentPath, state.layout) as DashComponent;
        return [c, c.props];
    };

export function selectDashPropsEqualityFn(
    [c, p]: SelectDashProps,
    [oc, op]: SelectDashProps
) {
    return p === op && c === oc;
}

export function selectConfig(state: any) {
    return state.config;
}
