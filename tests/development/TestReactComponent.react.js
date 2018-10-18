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
    /**
     * Description of optionalArray
     */
    optionalArray: PropTypes.array,
    optionalBool: PropTypes.bool,
    optionalFunc: PropTypes.func,
    optionalNumber: PropTypes.number,
    optionalObject: PropTypes.object,
    optionalString: PropTypes.string,
    optionalSymbol: PropTypes.symbol,

    // Anything that can be rendered: numbers, strings, elements or an array
    // (or fragment) containing these types.
    optionalNode: PropTypes.node,

    // A React element.
    optionalElement: PropTypes.element,

    // You can also declare that a prop is an instance of a class. This uses
    // JS's instanceof operator.
    optionalMessage: PropTypes.instanceOf(Message),

    // You can ensure that your prop is limited to specific values by treating
    // it as an enum.
    optionalEnum: PropTypes.oneOf(['News', 'Photos', 1, 2, true, false]),

    // An object that could be one of many types.
    optionalUnion: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
        PropTypes.instanceOf(Message)
    ]),

    // An array of a certain type
    optionalArrayOf: PropTypes.arrayOf(PropTypes.number),

    // An object with property values of a certain type
    optionalObjectOf: PropTypes.objectOf(PropTypes.number),

    // An object taking on a particular shape
    optionalObjectWithShapeAndNestedDescription: PropTypes.shape({
        color: PropTypes.string,
        fontSize: PropTypes.number,
        /**
         * Figure is a plotly graph object
         */
        figure: PropTypes.shape({
            /**
             * data is a collection of traces
             */
            data: PropTypes.arrayOf(PropTypes.object),
            /**
             * layout describes the rest of the figure
             */
            layout: PropTypes.object
        })
    }),

    // A value of any data type
    optionalAny: PropTypes.any,

    "data-*": PropTypes.string,
    "aria-*": PropTypes.string,

    customProp: function(props, propName, componentName) {
        if (!/matchme/.test(props[propName])) {
            return new Error(
            'Invalid prop `' + propName + '` supplied to' +
            ' `' + componentName + '`. Validation failed.'
            );
        }
    },

    customArrayProp: PropTypes.arrayOf(function(propValue, key, componentName, location, propFullName) {
        if (!/matchme/.test(propValue[key])) {
            return new Error(
            'Invalid prop `' + propFullName + '` supplied to' +
            ' `' + componentName + '`. Validation failed.'
            );
        }
    }),

    // special dash events

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

    in: PropTypes.string,
    id: PropTypes.string,


    // dashEvents is a special prop that is used to events validation
    dashEvents: PropTypes.oneOf([
        'restyle',
        'relayout',
        'click'
    ])
};

ReactComponent.defaultProps = {
    optionalNumber: 42,
    optionalString: 'hello world'
};

export default ReactComponent;
