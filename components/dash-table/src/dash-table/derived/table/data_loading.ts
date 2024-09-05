import {ILoadingState} from 'dash-table/components/Table/props';

export default function dataLoading(loading_state: ILoadingState | undefined) {
    return loading_state &&
        loading_state.is_loading &&
        (loading_state.prop_name === 'data' ||
            loading_state.prop_name === '' ||
            loading_state.prop_name === undefined)
        ? true
        : false;
}
