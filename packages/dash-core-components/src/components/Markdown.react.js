import React, {PropTypes} from 'react';
import Markdown from 'react-markdown';

/**
 * A component that renders Markdown text as specified by the
 * CommonMark spec.
 */
function DashMarkdown (props) {

    // must be a string or an array of strings
    if(typeof props.children !== 'string') {
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
    children: PropTypes.oneOfType([PropTypes.string, PropTypes.arrayOf(PropTypes.string)])
}

export default DashMarkdown;
