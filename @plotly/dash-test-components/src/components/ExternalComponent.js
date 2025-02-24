import React from 'react';
import PropTypes from 'prop-types';


const ExternalComponent = ({ id, text, input_id, extra_component }) => {
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
                componentPath={[...ctx.componentPath, 'external']}
            />}
            {
                extra_component &&
                <ExternalWrapper
                    component={extra_component}
                    componentPath={[...ctx.componentPath, 'extra']}
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
};

export default ExternalComponent;
