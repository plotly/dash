
import React, {PropTypes} from 'react';

const Ul = (props) => (
    <ul {...props}>
        {props.children}
    </ul>
);

Ul.propTypes = {

    /**
     * Defines a keyboard shortcut to activate or add focus to the element.
     */
    'accesskey': PropTypes.string,
        

    /**
     * Often used with CSS to style elements with common properties.
     */
    'className': PropTypes.string,
        

    /**
     * Indicates whether the element's content is editable.
     */
    'contenteditable': PropTypes.string,
        

    /**
     * Defines the ID of a <menu> element which will serve as the element's context menu.
     */
    'contextmenu': PropTypes.string,
        

    /**
     * Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)
     */
    'dir': PropTypes.string,
        

    /**
     * Defines whether the element can be dragged.
     */
    'draggable': PropTypes.string,
        

    /**
     * Indicates that the element accept the dropping of content on it.
     */
    'dropzone': PropTypes.string,
        

    /**
     * Prevents rendering of given element, while keeping child elements, e.g. script elements, active.
     */
    'hidden': PropTypes.string,
        

    /**
     * Often used with CSS to style a specific element. The value of this attribute must be unique.
     */
    'id': PropTypes.string,
        

    /**
     * 
     */
    'itemprop': PropTypes.string,
        

    /**
     * Defines the language used in the element.
     */
    'lang': PropTypes.string,
        

    /**
     * Indicates whether spell checking is allowed for the element.
     */
    'spellcheck': PropTypes.string,
        

    /**
     * Defines CSS styles which will override styles previously set.
     */
    'style': PropTypes.string,
        

    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    'tabindex': PropTypes.string,
        

    /**
     * Text to be displayed in a tooltip when hovering over the element.
     */
    'title': PropTypes.string
        
};

export default Ul;
    