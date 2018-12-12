
import React from 'react';
import PropTypes from 'prop-types';

const Video = (props) => {
    return (
        <video
            onClick={() => {
                if (props.setProps) {
                    props.setProps({
                        n_clicks: props.n_clicks + 1,
                        n_clicks_timestamp: Date.now()
                    })
                }
                if (props.fireEvent) props.fireEvent({event: 'click'});
            }}
            {...props}
        >
            {props.children}
        </video>
    );
};

Video.defaultProps = {
    n_clicks: 0,
    n_clicks_timestamp: -1
};

Video.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    'id': PropTypes.string,

    /**
     * The children of this component
     */
    'children': PropTypes.node,

    /**
     * An integer that represents the number of times
     * that this element has been clicked on.
     */
    'n_clicks': PropTypes.integer,

    /**
     * An integer that represents the time (in ms since 1970)
     * at which n_clicks changed. This can be used to tell
     * which button was changed most recently.
     */
    'n_clicks_timestamp': PropTypes.integer,

    /**
     * A unique identifier for the component, used to improve
     * performance by React.js while rendering components
     * See https://reactjs.org/docs/lists-and-keys.html for more info
     */
    'key': PropTypes.string,

    /**
     * The ARIA role attribute
     */
    'role': PropTypes.string,

    /**
     * A wildcard data attribute
     */
    'data-*': PropTypes.string,

    /**
     * A wildcard aria attribute
     */
    'aria-*': PropTypes.string,
    

    /**
     * The audio or video should play as soon as possible.
     */
    'autoPlay': PropTypes.string,

    /**
     * Indicates whether the browser should show playback controls to the user.
     */
    'controls': PropTypes.string,

    /**
     * How the element handles cross-origin requests
     */
    'crossOrigin': PropTypes.string,

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS height property should be used instead.
     */
    'height': PropTypes.string,

    /**
     * Indicates whether the media should start playing from the start when it's finished.
     */
    'loop': PropTypes.string,

    /**
     * Indicates whether the audio will be initially silenced on page load.
     */
    'muted': PropTypes.string,

    /**
     * A URL indicating a poster frame to show until the user plays or seeks.
     */
    'poster': PropTypes.string,

    /**
     * Indicates whether the whole resource, parts of it or nothing should be preloaded.
     */
    'preload': PropTypes.string,

    /**
     * The URL of the embeddable content.
     */
    'src': PropTypes.string,

    /**
     * For the elements listed here, this establishes the element's width.        Note: For all other instances, such as <div>, this is a legacy attribute, in which case the CSS width property should be used instead.
     */
    'width': PropTypes.string,

    /**
     * Defines a keyboard shortcut to activate or add focus to the element.
     */
    'accessKey': PropTypes.string,

    /**
     * Often used with CSS to style elements with common properties.
     */
    'className': PropTypes.string,

    /**
     * Indicates whether the element's content is editable.
     */
    'contentEditable': PropTypes.string,

    /**
     * Defines the ID of a <menu> element which will serve as the element's context menu.
     */
    'contextMenu': PropTypes.string,

    /**
     * Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)
     */
    'dir': PropTypes.string,

    /**
     * Defines whether the element can be dragged.
     */
    'draggable': PropTypes.string,

    /**
     * Prevents rendering of given element, while keeping child elements, e.g. script elements, active.
     */
    'hidden': PropTypes.string,

    /**
     * Defines the language used in the element.
     */
    'lang': PropTypes.string,

    /**
     * Indicates whether spell checking is allowed for the element.
     */
    'spellCheck': PropTypes.string,

    /**
     * Defines CSS styles which will override styles previously set.
     */
    'style': PropTypes.object,

    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    'tabIndex': PropTypes.string,

    /**
     * Text to be displayed in a tooltip when hovering over the element.
     */
    'title': PropTypes.string,

    /**
     * A callback for firing events to dash.
     */
    'fireEvent': PropTypes.func,

    'dashEvents': PropTypes.oneOf(['click']),
    
    'setProps': PropTypes.func
    
};

export default Video;
