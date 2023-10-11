import {batch} from 'react-redux';
import {setGraphs} from './index';
import apiThunk from './api';

export function requestDependencies() {
    return (dispatch: any) => {
        batch(() => {
            dispatch(setGraphs({}));
            dispatch(
                apiThunk('_dash-dependencies', 'GET', 'dependenciesRequest')
            );
        });
    };
}
