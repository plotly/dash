import {path, type, has} from 'ramda';

import Registry from '../registry';
import {stringifyId} from '../actions/dependencies';

function isLoadingComponent(layout: any) {
    validateComponent(layout);
    return (Registry.resolve(layout) as any)._dashprivate_isLoadingComponent;
}

const NULL_LOADING_STATE = false;

export function getLoadingState(
    componentLayout: any,
    componentPath: any,
    loadingMap: any
) {
    if (!loadingMap) {
        return NULL_LOADING_STATE;
    }

    const loadingFragment: any = path(componentPath, loadingMap);
    // Component and children are not loading if there's no loading fragment
    // for the component's path in the layout.
    if (!loadingFragment) {
        return NULL_LOADING_STATE;
    }

    const idprop: any = loadingFragment.__dashprivate__idprop__;
    if (idprop) {
        return {
            is_loading: true,
            prop_name: idprop.property,
            component_name: stringifyId(idprop.id)
        };
    }

    const idprops: any = loadingFragment.__dashprivate__idprops__?.[0];
    if (idprops && isLoadingComponent(componentLayout)) {
        return {
            is_loading: true,
            prop_name: idprops.property,
            component_name: stringifyId(idprops.id)
        };
    }

    return NULL_LOADING_STATE;
}

export const getLoadingHash = (componentPath: any, loadingMap: any) =>
    (
        ((loadingMap &&
            (path(componentPath, loadingMap) as any)
                ?.__dashprivate__idprops__) ??
            []) as any[]
    )
        .map(({id, property}) => `${id}.${property}`)
        .join(',');

export function validateComponent(componentDefinition: any) {
    if (type(componentDefinition) === 'Array') {
        throw new Error(
            'The children property of a component is a list of lists, instead ' +
                'of just a list. ' +
                'Check the component that has the following contents, ' +
                'and remove one of the levels of nesting: \n' +
                JSON.stringify(componentDefinition, null, 2)
        );
    }
    if (
        type(componentDefinition) === 'Object' &&
        !(
            has('namespace', componentDefinition) &&
            has('type', componentDefinition) &&
            has('props', componentDefinition)
        )
    ) {
        throw new Error(
            'An object was provided as `children` instead of a component, ' +
                'string, or number (or list of those). ' +
                'Check the children property that looks something like:\n' +
                JSON.stringify(componentDefinition, null, 2)
        );
    }
}
