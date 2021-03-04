import PropTypes from 'prop-types';
import {Component} from 'react';
import {toByteArray} from 'base64-js';
import {saveAs} from 'file-saver';

const getValue = (src, fallback, key) =>
    key in src ? src[key] : fallback[key];

/**
 * The Download component opens a download dialog when the data property changes.
 */
export default class Download extends Component {
    componentDidUpdate(prevProps) {
        const {data} = this.props;
        // If the data hasn't changed, do nothing.
        if (!data || data === prevProps.data) {
            return;
        }
        // Extract options from data if provided, fallback to props.
        const type = getValue(data, this.props, 'type');
        const base64 = getValue(data, this.props, 'base64');
        // Invoke the download using a Blob.
        const content = base64 ? toByteArray(data.content) : data.content;
        const blob = new Blob([content], {type: type});
        saveAs(blob, data.filename);
    }

    render() {
        return null;
    }
}

Download.propTypes = {
    /**
     * The ID of this component, used to identify dash components in callbacks.
     */
    id: PropTypes.string,

    /**
     * On change, a download is invoked.
     */
    data: PropTypes.exact({
        /**
         * Suggested filename in the download dialogue.
         */
        filename: PropTypes.string.isRequired,
        /**
         * File content.
         */
        content: PropTypes.string.isRequired,
        /**
         * Set to true, when data is base64 encoded.
         */
        base64: PropTypes.bool,
        /**
         * Blob type, usually a MIME-type.
         */
        type: PropTypes.string,
    }),

    /**
     * Default value for base64, used when not set as part of the data property.
     */
    base64: PropTypes.bool,

    /**
     * Default value for type, used when not set as part of the data property.
     */
    type: PropTypes.string,

    /**
     * Dash-supplied function for updating props.
     */
    setProps: PropTypes.func,
};

Download.defaultProps = {
    type: 'text/plain',
    base64: false,
};
