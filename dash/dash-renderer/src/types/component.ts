import {
    DashContext,
    DashContextProviderProps,
    useDashContext
} from '../wrapper/DashContext';
import ExternalWrapper from '../wrapper/ExternalWrapper';
import {stringifyId} from '../actions/dependencies';

export type BaseDashProps = {
    id?: string;
    componentPath?: DashLayoutPath;
    [key: string]: any;
};

export interface DashComponentApi {
    ExternalWrapper: typeof ExternalWrapper;
    DashContext: typeof DashContext;
    useDashContext: typeof useDashContext;
    getLayout: (componentPathOrId: DashLayoutPath | string) => DashComponent;
    stringifyId: typeof stringifyId;
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
