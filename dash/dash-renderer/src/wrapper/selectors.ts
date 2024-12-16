import {path} from 'ramda';

import {
    DashLayoutPath,
    DashComponent,
    BaseDashProps,
    DashLoadingState
} from '../types/component';
import {getLoadingState} from './wrapping';

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

export const selectLoadingState =
    (componentPath: DashLayoutPath) => (state: any) => {
        const component = path(componentPath, state.layout);
        return getLoadingState(component, componentPath, state.loadingMap);
    };

export function selectLoadingStateEqualityFn(
    lhs: DashLoadingState,
    rhs: DashLoadingState
) {
    return (
        rhs.is_loading === lhs.is_loading &&
        lhs.component_name == rhs.component_name &&
        rhs.prop_name == lhs.prop_name
    );
}

export function selectConfig(state: any) {
    return state.config;
}
