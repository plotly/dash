import React from 'react';
// A react component with all of the available proptypes to run tests over

/**
 * This is a description of the component.
 * It's multiple lines long.
 */
class ReactComponent extends Component {
    render() {
        return '';
    }
}

ReactComponent.propTypes = {
    children: React.PropTypes.node,
    id: React.PropTypes.string.isRequired,
};

export default ReactComponent;
