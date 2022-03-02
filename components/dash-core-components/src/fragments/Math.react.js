import PropTypes from 'prop-types';
import React, {Component} from 'react';

export default class DashMath extends Component {
    constructor(props) {
        super(props);
        this.span_element = React.createRef();
    }

    componentDidMount() {
        this.renderMath();
    }

    componentDidUpdate(prevProps) {
        if (
            prevProps.tex !== this.props.tex ||
            prevProps.inline !== this.props.inline
        ) {
            this.renderMath();
        }
    }

    renderMath() {
        if (window.MathJax?.typeset) {
            window.MathJax.typeset([this.span_element.current]);
        }
    }

    render() {
        return (
            <span ref={this.span_element}>
                {this.props.inline ? String.raw`\(` : String.raw`\[`}
                {this.props.tex}
                {this.props.inline ? String.raw`\)` : String.raw`\]`}
            </span>
        );
    }
}

DashMath.propTypes = {
    tex: PropTypes.string,
    inline: PropTypes.bool,
};

DashMath.defaultProps = {
    tex: '',
    inline: true,
};

export const propTypes = DashMath.propTypes;
export const defaultProps = DashMath.defaultProps;
