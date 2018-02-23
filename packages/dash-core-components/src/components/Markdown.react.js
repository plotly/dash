import React from 'react';
import PropTypes from 'prop-types';
import {type} from 'ramda';
import Markdown from 'react-markdown';

/**
 * A component that renders Markdown text as specified by the
 * CommonMark spec.
 */
function DashMarkdown (props) {

    if(type(props.children) === 'Array') {
        props.children = props.children.join('\n');
    }

    return (
        <Markdown
            source={props.children}
            escapeHtml={true}
            {...props}
        />
    )
}

DashMarkdown.propTypes = {
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
     * A markdown string (or array of strings) that adhreres to the CommonMark spec
     */
    children: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string)
    ])
};

export default DashMarkdown;
