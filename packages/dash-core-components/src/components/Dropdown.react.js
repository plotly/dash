import React, {Component, PropTypes} from 'react';

/*
 * A controlled input that calls `valueChanged` on changes.
 */
export default class Dropdown extends Component {
    handleChange(value) {
        this.props.valueChanged({value});
    }

    renderOptions() {
        const {options} = this.props;

        return options.map((option) => (
            <option
                key={option.value}
                value={option.value}
            >
                {option.label}
            </option>
        ));
    }

    render() {
        const {value} = this.props;

        return (
            <select
                value={value}
                onChange={ev => this.handleChange(ev.target.value)}
            >
                {this.renderOptions()}

            </select>
        )
    }
}

Dropdown.propTypes = {

    /**
     * Function that updates the state tree.
     */
    valueChanged: PropTypes.func,

    /**
     * Options
     */
    options: React.PropTypes.arrayOf(
        React.PropTypes.shape({
            value: React.PropTypes.string.isRequired,
            label: React.PropTypes.string.isRequired
        })
    ),

    /**
     * Selected value
     */
    value: React.PropTypes.string
};

Dropdown.defaultProps = {
    valueChanged: () => {},
    options: [],
    value: ''
};
