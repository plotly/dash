import {arduinoLight, monokai} from 'react-syntax-highlighter/dist/styles';
import PropTypes from 'prop-types';
import {omit, type} from 'ramda';
import React from 'react';
import ReactSyntaxHighlighter from 'react-syntax-highlighter';

// eslint-disable-next-line valid-jsdoc
/**
 * A component for pretty printing code.
 */
export default function SyntaxHighlighter(props) {
    const {id, theme, loading_state} = props;
    let style;
    if (theme === 'dark') {
        style = monokai;
    } else {
        style = arduinoLight;
    }

    // must be a string or an array of strings
    if (type(props.children) === 'Array') {
        props.children = props.children.join('\n');
    }
    if (type(props.children) === 'Null') {
        props.children = '';
    }
    return (
        <div
            id={id}
            data-dash-is-loading={
                (loading_state && loading_state.is_loading) || undefined
            }
        >
            <ReactSyntaxHighlighter style={style} {...omit(['theme'], props)} />
        </div>
    );
}

SyntaxHighlighter.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,
    /**
     * The text to display and highlight
     */
    children: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * the language to highlight code in.
     */
    language: PropTypes.string,
    /**
     * theme: light or dark
     */
    theme: PropTypes.oneOf(['light', 'dark']),

    /**
     * prop that will be combined with the top level style on the pre tag, styles here will overwrite earlier styles.
     */
    customStyle: PropTypes.object,
    /**
     * props that will be spread into the <code> tag that is the direct parent of the highlighted code elements. Useful for styling/assigning classNames.
     */
    codeTagProps: PropTypes.object,
    /**
     * if this prop is passed in as false, react syntax highlighter will not add style objects to elements, and will instead append classNames. You can then style the code block by using one of the CSS files provided by highlight.js.
     */
    useInlineStyles: PropTypes.bool,
    /**
     * if this is enabled line numbers will be shown next to the code block.
     */
    showLineNumbers: PropTypes.bool,
    /**
     * if showLineNumbers is enabled the line numbering will start from here.
     */
    startingLineNumber: PropTypes.number,
    /**
     * the line numbers container default to appearing to the left with 10px of right padding. You can use this to override those styles.
     */
    lineNumberContainerStyle: PropTypes.object,
    /**
     * inline style to be passed to the span wrapping each number. Can be either an object or a function that recieves current line number as argument and returns style object.
     */
    lineNumberStyle: PropTypes.object,
    /**
     * a boolean value that determines whether or not each line of code should be wrapped in a parent element. defaults to false, when false one can not take action on an element on the line level. You can see an example of what this enables here
     */
    wrapLines: PropTypes.bool,
    /**
     * inline style to be passed to the span wrapping each line if wrapLines is true. Can be either an object or a function that recieves current line number as argument and returns style object.
     */
    lineStyle: PropTypes.object,
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

SyntaxHighlighter.defaultProps = {};
