import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {type} from 'ramda';
import Markdown from 'react-markdown';
import './css/highlight.css';

// eslint-disable-next-line valid-jsdoc
/**
 * A component that renders Markdown text as specified by the
 * GitHub Markdown spec. These component uses
 * [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
 */
class DashMarkdown extends Component {
    constructor(props) {
        super(props);
        this.highlightCode = this.highlightCode.bind(this);
        this.dedent = this.dedent.bind(this);
    }

    componentDidMount() {
        this.highlightCode();
    }

    componentDidUpdate() {
        this.highlightCode();
    }

    highlightCode() {
        if (!window.hljs) {
            // skip highlighting if highlight.js isn't found
            return;
        }
        if (this.mdContainer) {
            const nodes = this.mdContainer.getElementsByTagName('code');

            for (let i = 0; i < nodes.length; i++) {
                window.hljs.highlightBlock(nodes[i]);
            }
        }
    }

    dedent(text) {
        const lines = text.split(/\r\n|\r|\n/);
        let commonPrefix = null;
        for (const line of lines) {
            const preMatch = line && line.match(/^\s*(?=\S)/);
            if (preMatch) {
                const prefix = preMatch[0];
                if (commonPrefix !== null) {
                    for (let i = 0; i < commonPrefix.length; i++) {
                        // Like Python's textwrap.dedent, we'll remove both
                        // space and tab characters, but only if they match
                        if (prefix[i] !== commonPrefix[i]) {
                            commonPrefix = commonPrefix.substr(0, i);
                            break;
                        }
                    }
                } else {
                    commonPrefix = prefix;
                }

                if (!commonPrefix) {
                    break;
                }
            }
        }

        const commonLen = commonPrefix ? commonPrefix.length : 0;
        return lines
            .map(line => {
                return line.match(/\S/) ? line.substr(commonLen) : '';
            })
            .join('\n');
    }

    render() {
        const {
            id,
            style,
            className,
            highlight_config,
            loading_state,
            dangerously_allow_html,
            children,
            dedent,
        } = this.props;

        const textProp =
            type(children) === 'Array' ? children.join('\n') : children;
        const displayText =
            dedent && textProp ? this.dedent(textProp) : textProp;

        return (
            <div
                id={id}
                ref={node => {
                    this.mdContainer = node;
                }}
                style={style}
                className={
                    ((highlight_config && highlight_config.theme) ||
                        className) &&
                    `${className ? className : ''} ${
                        highlight_config &&
                        highlight_config.theme &&
                        highlight_config.theme === 'dark'
                            ? 'hljs-dark'
                            : ''
                    }`
                }
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
            >
                <Markdown
                    source={displayText}
                    escapeHtml={!dangerously_allow_html}
                />
            </div>
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
     * A boolean to control raw HTML escaping.
     * Setting HTML from code is risky because it's easy to
     * inadvertently expose your users to a cross-site scripting (XSS)
     * (https://en.wikipedia.org/wiki/Cross-site_scripting) attack.
     */
    dangerously_allow_html: PropTypes.bool,

    /**
     * A markdown string (or array of strings) that adhreres to the CommonMark spec
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
    dangerously_allow_html: false,
    highlight_config: {},
    dedent: true,
};

export default DashMarkdown;
