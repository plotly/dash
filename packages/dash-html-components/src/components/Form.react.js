
import React, {PropTypes} from 'react';

const Form = (props) => {
    if (props.fireEvent) {
        return (
            <form
                onClick={() => props.fireEvent({event: 'click'})}
                {...props}
            >
                {props.children}
            </form>
        );
    } else {
        return (
            <form {...props}>
                {props.children}
            </form>
        );
    }
};

Form.propTypes = {

    /**
     * List of types the server accepts, typically a file type.
     */
    'accept': PropTypes.string,

    /**
     * List of supported charsets.
     */
    'acceptCharset': PropTypes.string,

    /**
     * The URI of a program that processes the information submitted via the form.
     */
    'action': PropTypes.string,

    /**
     * Indicates whether controls in this form can by default have their values automatically completed by the browser.
     */
    'autoComplete': PropTypes.string,

    /**
     * Defines the content type of the form date when the method is POST.
     */
    'encType': PropTypes.string,

    /**
     * Defines which HTTP method to use when submitting the form. Can be GET (default) or POST.
     */
    'method': PropTypes.string,

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,

    /**
     * This attribute indicates that the form shouldn't be validated when submitted.
     */
    'noValidate': PropTypes.string,

    /**
     *
     */
    'target': PropTypes.string,

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
    'content': PropTypes.node,

    /**
     * A callback for firing events to dash.
     */
    'fireEvent': PropTypes.func,

    'dashEvents': PropTypes.oneOf(['click'])
    
};

export default Form;
