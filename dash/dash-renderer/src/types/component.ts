import {
    DashContext,
    DashContextProviderProps,
    useDashContext
} from '../wrapper/DashContext';
import ExternalWrapper from '../wrapper/ExternalWrapper';
import {stringifyId} from '../actions/dependencies';
import {
    DevtoolContext,
    useDevtool,
    useDevtoolMenuButtonClassName
} from '../components/error/menu/DevtoolContext';

// Caution: These docstrings appear in the published documentation!
export type BaseDashProps = {
    /**
     * The ID of this component, used to identify dash components in callbacks.
     * The ID needs to be unique across all of the components in an app.
     */
    id?: string;
    componentPath?: DashLayoutPath;
    [key: string]: any;
};

export interface DashComponentApi {
    ExternalWrapper: typeof ExternalWrapper;
    DashContext: typeof DashContext;
    useDashContext: typeof useDashContext;
    getLayout: (componentPathOrId: DashLayoutPath | string) => any;
    stringifyId: typeof stringifyId;
    devtool: {
        DevtoolContext: typeof DevtoolContext;
        useDevtool: typeof useDevtool;
        useDevtoolMenuButtonClassName: typeof useDevtoolMenuButtonClassName;
    };
}

export type DashComponent = {
    type: string;
    namespace: string;
    props: DashContextProviderProps & BaseDashProps;
};

export type UpdatePropsPayload = {
    _dash_error?: any;
    [key: string]: any;
};

export type EnhancedDashProps =
    | BaseDashProps
    | {
          setProps: (props: any) => void;
      };

// Layout is either a component of a list of components.
export type DashLayout = DashComponent[] | DashComponent;

export type DashLayoutPath = (string | number)[];

export type DashLoadingState = {
    is_loading: boolean;
    prop_name?: string;
    component_name?: string;
};
