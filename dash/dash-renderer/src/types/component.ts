export type BaseDashProps = {
    id?: string;
    [key: string]: any;
};

export type DashComponent = {
    type: string;
    namespace: string;
    props: BaseDashProps;
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
