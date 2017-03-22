
import React, {PropTypes} from 'react';

const Textarea = (props) => {
    if (props.fireEvent) {
        return (
            <textarea
                onClick={() => props.fireEvent({event: 'click'})}
                onMouseEnter={() => props.fireEvent({event: 'mouseEnter'})}
                onMouseLeave={() => props.fireEvent({event: 'mouseLeave'})}
                {...props}
            >
                {props.children}
            </textarea>
        );
    } else {
        return (
            <textarea {...props}>
                {props.children}
            </textarea>
        );
    }
};

Textarea.propTypes = {

    /**
     * The element should be automatically focused after the page loaded.
     */
    'autoFocus': PropTypes.string,

    /**
     * Defines the number of columns in a textarea.
     */
    'cols': PropTypes.string,

    /**
     * Indicates whether the user can interact with the element.
     */
    'disabled': PropTypes.string,

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    'maxLength': PropTypes.string,

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,

    /**
     * Provides a hint to the user of what can be entered in the field.
     */
    'placeholder': PropTypes.string,

    /**
     * Indicates whether the element can be edited.
     */
    'readOnly': PropTypes.string,

    /**
     * Indicates whether this element is required to fill out or not.
     */
    'required': PropTypes.string,

    /**
     * Defines the number of rows in a text area.
     */
    'rows': PropTypes.string,

    /**
     * Indicates whether the text should be wrapped.
     */
    'wrap': PropTypes.string,

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
     * A callback for firing events to dash.
     */
    'fireEvent': PropTypes.func,

    'dashEvents': PropTypes.oneOf(['click', 'mouseEnter', 'mouseLeave'])
    
};

export default Textarea;
