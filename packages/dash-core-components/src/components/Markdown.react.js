import React from 'react';
import PropTypes from 'prop-types';
import {omit, propOr, type} from 'ramda';
import Markdown from 'react-markdown';

// eslint-disable-next-line valid-jsdoc
/**
 * A component that renders Markdown text as specified by the
 * GitHub Markdown spec. These component uses
 * [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
 */
function DashMarkdown(props) {
    if (type(props.children) === 'Array') {
        props.children = props.children.join('\n');
    }

    return (
        <div
            id={props.id}
            data-dash-is-loading={
                (props.loading_state && props.loading_state.is_loading) ||
                undefined
            }
            {...propOr({}, 'containerProps', props)}
        >
            <Markdown
                source={props.children}
                escapeHtml={!props.dangerously_allow_html}
                {...omit(['containerProps'], props)}
            />
        </div>
    );
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
     * An object containing custom element props to put on the container
     * element such as id or style
     */
    containerProps: PropTypes.object,

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
};

DashMarkdown.defaultProps = {
    dangerously_allow_html: false,
};

export default DashMarkdown;
