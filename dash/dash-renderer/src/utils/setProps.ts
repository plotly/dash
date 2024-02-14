import {updateProps, notifyObservers} from '../actions/index';

const makeSetProps = ({dispatch, getState}) => {
    const setProps = (updates: {}) => {
        const {paths} = getState();
        Object.entries(updates).forEach(([componentId, props]) => {
            const componentPath = paths.strs[componentId];
            dispatch(
                updateProps({
                    props,
                    itempath: componentPath
                })
            );
            dispatch(notifyObservers({id: componentId, props}));
        });
    };

    window.dash_clientside = window.dash_clientside || {};
    window.dash_clientside['setProps'] = setProps;
};

export default makeSetProps;
