import React from 'react';
import PropTypes from 'prop-types';


const ExternalComponent = ({ id, text, input_id }) => {
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
        </div>
    )
}

ExternalComponent.propTypes = {
    id: PropTypes.string,
    text: PropTypes.string,
    input_id: PropTypes.string,
};

export default ExternalComponent;
