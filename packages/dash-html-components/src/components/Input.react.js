
import React, {PropTypes} from 'react';

const Input = (props) => (
    <input {...props}>
        {props.children}
    </input>
);

Input.propTypes = {

    /**
     * List of types the server accepts, typically a file type.
     */
    'accept': PropTypes.string,

    /**
     * Alternative text in case an image can't be displayed.
     */
    'alt': PropTypes.string,

    /**
     * Indicates whether controls in this form can by default have their values automatically completed by the browser.
     */
    'autoComplete': PropTypes.string,

    /**
     * The element should be automatically focused after the page loaded.
     */
    'autoFocus': PropTypes.string,

    /**
     * Indicates whether the element should be checked on page load.
     */
    'checked': PropTypes.string,

    /**
     * Indicates whether the user can interact with the element.
     */
    'disabled': PropTypes.string,

    /**
     * Indicates the form that is the owner of the element.
     */
    'form': PropTypes.string,

    /**
     * Indicates the action of the element, overriding the action defined in the <form>.
     */
    'formAction': PropTypes.string,

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS height property should be used instead.
     */
    'height': PropTypes.string,

    /**
     * Identifies a list of pre-defined options to suggest to the user.
     */
    'list': PropTypes.string,

    /**
     * Indicates the maximum value allowed.
     */
    'max': PropTypes.string,

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    'maxLength': PropTypes.string,

    /**
     * Indicates the minimum value allowed.
     */
    'min': PropTypes.string,

    /**
     * Indicates whether multiple values can be entered in an input of the type email or file.
     */
    'multiple': PropTypes.string,

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    'name': PropTypes.string,

    /**
     * Defines a regular expression which the element's value will be validated against.
     */
    'pattern': PropTypes.string,

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
     * Defines the width of the element (in pixels). If the element's type attribute is text or password then it's the number of characters.
     */
    'size': PropTypes.string,

    /**
     * The URL of the embeddable content.
     */
    'src': PropTypes.string,

    /**
     *
     */
    'step': PropTypes.string,

    /**
     * Defines the type of the element.
     */
    'type': PropTypes.string,

    /**
     *
     */
    'useMap': PropTypes.string,

    /**
     * Defines a default value which will be displayed in the element on page load.
     */
    'value': PropTypes.string,

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
     * Often used with CSS to style a specific element. The value of this attribute must be unique.
     */
    'id': PropTypes.string,

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
    'style': PropTypes.string,

    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    'tabIndex': PropTypes.string,

    /**
     * Text to be displayed in a tooltip when hovering over the element.
     */
    'title': PropTypes.string
};

export default Input;
