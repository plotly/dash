import React from 'react';
import PropTypes from 'prop-types';


const ExternalComponent = ({ id, text, input_id, extra_component }) => {
    const ctx = window.dash_component_api.useDashContext();
    const ExternalWrapper = window.dash_component_api.ExternalWrapper;

    return (
        <div id={id}>
            <ExternalWrapper
                id={input_id}
                componentType="Input"
                componentNamespace="dash_core_components"
                value={text}
                componentPath={[...ctx.componentPath, 'external']}
            />
            {
                extra_component &&
                <ExternalWrapper
                    componentType={extra_component.type}
                    componentNamespace={extra_component.namespace}
                    componentPath={[...ctx.componentPath, 'extra']}
                    {...extra_component.props}
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
