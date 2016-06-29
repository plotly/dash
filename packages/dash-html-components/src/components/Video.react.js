
import React, {PropTypes} from 'react';

const Video = (props) => (
    <video {...props}>
        {props.children}
    </video>
);

Video.propTypes = {

    /**
     * The audio or video should play as soon as possible.
     */
    'autoplay': PropTypes.string,
        

    /**
     * Contains the time range of already buffered media.
     */
    'buffered': PropTypes.string,
        

    /**
     * Indicates whether the browser should show playback controls to the user.
     */
    'controls': PropTypes.string,
        

    /**
     * Specifies the height of elements listed here. For all other elements, use the CSS height property.        Note: In some instances, such as <div>, this is a legacy attribute, in which case the CSS heightproperty should be used instead.
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
     * For the elements listed here, this establishes the element's width.        Note: For all other instances, such as <div>, this is a legacy attribute, in which case the CSS widthproperty should be used instead.
     */
    'width': PropTypes.string
        
};

export default Video;
    