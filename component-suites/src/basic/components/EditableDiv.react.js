/*
 * Example of a pretty generic editable component.
 * These types of components would live in their own set of modules ("component suites").
 * This component illustrates how the `onPropUpdate` prop can be used
 */


import R from 'ramda';
import Radium from 'radium';
import React, { PropTypes } from 'react';
import ReactDOM from 'react-dom';

// each suite might have its own set of Styles
import Styles from '../Styles';

const baseStyles = {
    color: Styles.colors.base,
    ':hover': {
        color: Styles.colors.baseHover
    }
}

class EditableDiv extends React.Component {

    constructor(props) {
        super(props);
        this.state = {inEditMode: false};
    }

    componentDidUpdate() {
        if (this.state.inEditMode) ReactDOM.findDOMNode(this.refs.input).focus();
    }

    render() {
        if (this.state.inEditMode) {
            return (
                <div>
                    <input
                        ref="input"
                        autofocus={true}
                        style={R.mergeAll([
                            {border: 'none', padding: 0, margin: 0},
                            baseStyles,
                            this.props.style
                        ])}
                        value={this.props.text}
                        onChange={(e) => this.props.updateProps({text: e.target.value})}
                        onBlur={() => this.setState({inEditMode: false})}
                    />
                </div>
            );
        }
        else {
            return (
                <div style={R.merge(baseStyles, this.props.style)}
                     onClick={() => {
                        if (this.props.editable) this.setState({inEditMode: true});
                    }}
                >
                    {this.props.text}
                </div>
            );
        }
    }

}

EditableDiv.propTypes = {
    // unique to this component
    text: PropTypes.string.isRequired, // the displayed text of this component
    style: PropTypes.object,           // the style of the text

    // Passed in from the renderer
    editable: PropTypes.bool,     // whether or not this component should be rendered as editable
    updateProps: PropTypes.func   // function that updates the state tree
};

EditableDiv.defaultProps = {
    text: ''
};

export default Radium(EditableDiv);
