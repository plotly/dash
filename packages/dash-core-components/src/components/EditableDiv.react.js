import R from 'ramda';
import React, {Component, PropTypes} from 'react';
import ReactDOM from 'react-dom';

// each suite might have its own set of Styles
import Styles from '../Styles';

const baseStyles = {
    color: Styles.colors.base,
    ':hover': {
        color: Styles.colors.baseHover
    }
};

/**
 * A div for displaying text. The text is editable.
 */
export default class EditableDiv extends Component {

    constructor(props) {
        super(props);

        this.state = {
            inEditMode: false
        };
    }

    componentDidUpdate() {
        if (this.state.inEditMode) {
            ReactDOM.findDOMNode(this.refs.input).focus();
        }
    }

    handleChange(text) {
        this.props.valueChanged({text});
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
                        onChange={(e) => this.handleChange(e.target.value)}
                        onBlur={() => this.setState({inEditMode: false})}
                    />
                </div>
            )
        }
        else {
            return (
                <div style={R.merge(baseStyles, this.props.style)}
                     onClick={() => {
                        if (this.props.editable) this.setState({inEditMode: true})
                    }}
                >
                    {this.props.text}
                </div>
            )
        }
    }

}

EditableDiv.propTypes = {

    /**
     * The displayed text of this component.
     */
    text: PropTypes.string.isRequired,

    /**
     * The style of the text.
     */
    style: PropTypes.object,

    /**
     * Whether or not this component should be rendered as editable.
     * Passed in from renderer.
     */
    editable: PropTypes.bool,

    /**
     * Function that updates the state tree.
     */
    valueChanged: PropTypes.func
};

EditableDiv.defaultProps = {
    style: {},
    editable: false,
    valueChanged: () => {}
};
