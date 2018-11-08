import React from 'react';
import PropTypes from 'prop-types';
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
    children: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
      PropTypes.bool,
      PropTypes.element,
      PropTypes.oneOf([null]),
      PropTypes.arrayOf(
        PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.number,
          PropTypes.bool,
        PropTypes.element,
          PropTypes.oneOf([null])
        ])
      )
    ]),
    id: PropTypes.string.isRequired,
};

export default ReactComponent;
