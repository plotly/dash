import React from 'react';
import PropTypes from 'prop-types';


const ExternalComponent = ({ id, text, input_id, extra_component, extra_component_temp }) => {
    const ctx = window.dash_component_api.useDashContext();
    const ExternalWrapper = window.dash_component_api.ExternalWrapper;
    return (
        <div id={id}>
            {text && <ExternalWrapper
                
                component={{
                    type: "Input",
                    namespace: "dash_core_components",
                    props: {
                        value: text,
                        id: input_id
                    }
                }}
                componentPath={[JSON.stringify(ctx.componentPath), 'text']}
                temp={true}
            />}
            {
                extra_component &&
                <ExternalWrapper
                    component={extra_component}
                    componentPath={[...ctx.componentPath, 'props', 'extra_component']}
                    temp={extra_component_temp}
            />}
        </div>
    )
}

ExternalComponent.propTypes = {
    id: PropTypes.string,
    text: PropTypes.string,
    input_id: PropTypes.string,
    extra_component: PropTypes.exact({
        type: PropTypes.string,
        namespace: PropTypes.string,
        props: PropTypes.object, 
    }),
    extra_component_temp: PropTypes.bool,
};

export default ExternalComponent;
