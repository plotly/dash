import {asyncDecorator} from '@plotly/dash-component-plugins';
import PropTypes from 'prop-types';
import React, {Component, Suspense} from 'react';
import markdown from '../utils/LazyLoader/markdown';
import lazyLoadMathJax from '../utils/LazyLoader/mathjax';

// eslint-disable-next-line valid-jsdoc
/**
 * A component that renders Markdown text as specified by the
 * GitHub Markdown spec. These component uses
 * [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
 */
export default class DashMarkdown extends Component {
    constructor(props) {
        super(props);

        if (props.mathjax) {
            DashMarkdown._loadMathjax = true;
        }
    }

    render() {
        return (
            <Suspense fallback={null}>
                <RealDashMarkdown {...this.props} />
            </Suspense>
        );
    }
}

DashMarkdown.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,
    /**
     * Class name of the container element
     */
    className: PropTypes.string,

    /**
     * If true, loads mathjax v3 (tex-svg) into the page and use it in the markdown
     */
    mathjax: PropTypes.bool,

    /**
     * A boolean to control raw HTML escaping.
     * Setting HTML from code is risky because it's easy to
     * inadvertently expose your users to a cross-site scripting (XSS)
     * (https://en.wikipedia.org/wiki/Cross-site_scripting) attack.
     */
    dangerously_allow_html: PropTypes.bool,

    /**
     * A string for the target attribute to use on links (such as "_blank")
     */
    link_target: PropTypes.string,

    /**
     * A markdown string (or array of strings) that adheres to the CommonMark spec
     */
    children: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * Remove matching leading whitespace from all lines.
     * Lines that are empty, or contain *only* whitespace, are ignored.
     * Both spaces and tab characters are removed, but only if they match;
     * we will not convert tabs to spaces or vice versa.
     */
    dedent: PropTypes.bool,

    /**
     * Config options for syntax highlighting.
     */
    highlight_config: PropTypes.exact({
        /**
         * Color scheme; default 'light'
         */
        theme: PropTypes.oneOf(['dark', 'light']),
    }),

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),

    /**
     * User-defined inline styles for the rendered Markdown
     */
    style: PropTypes.object,
};

DashMarkdown.defaultProps = {
    mathjax: false,
    dangerously_allow_html: false,
    highlight_config: {},
    dedent: true,
};

const RealDashMarkdown = asyncDecorator(DashMarkdown, () =>
    Promise.all([
        markdown(),
        DashMarkdown._loadMathjax ? lazyLoadMathJax() : undefined,
    ]).then(([md]) => md)
);

export const propTypes = DashMarkdown.propTypes;
export const defaultProps = DashMarkdown.defaultProps;
