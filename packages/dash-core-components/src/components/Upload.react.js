import PropTypes from 'prop-types';
import React, {Component} from 'react';
import Dropzone from 'react-dropzone';

/**
 * Upload components allow your app to accept user-uploaded files via drag'n'drop
 */
export default class Upload extends Component {
    constructor() {
        super();
        this.onDrop = this.onDrop.bind(this);
    }

    onDrop(files) {
        const {multiple, setProps} = this.props;
        const newProps = {
            contents: [],
            filename: [],
            last_modified: [],
        };
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                /*
                 * I'm not sure if reader.onload will be executed in order.
                 * For example, if the 1st file is larger than the 2nd one,
                 * the 2nd file might load first.
                 */
                newProps.contents.push(reader.result);
                newProps.filename.push(file.name);
                // eslint-disable-next-line no-magic-numbers
                newProps.last_modified.push(file.lastModified / 1000);
                if (newProps.contents.length === files.length) {
                    if (multiple) {
                        setProps(newProps);
                    } else {
                        setProps({
                            contents: newProps.contents[0],
                            filename: newProps.filename[0],
                            last_modified: newProps.last_modified[0],
                        });
                    }
                }
            };
            reader.readAsDataURL(file);
        });
    }

    render() {
        const {
            id,
            children,
            accept,
            disabled,
            disable_click,
            max_size,
            min_size,
            multiple,
            className,
            className_active,
            className_reject,
            className_disabled,
            style,
            style_active,
            style_reject,
            style_disabled,
            loading_state,
        } = this.props;
        return (
            <div
                id={id}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
            >
                <Dropzone
                    onDrop={this.onDrop}
                    accept={accept}
                    disabled={disabled}
                    disableClick={disable_click}
                    maxSize={max_size === -1 ? Infinity : max_size}
                    minSize={min_size}
                    multiple={multiple}
                    className={className}
                    activeClassName={className_active}
                    rejectClassName={className_reject}
                    disabledClassName={className_disabled}
                    style={style}
                    activeStyle={style_active}
                    rejectStyle={style_reject}
                    disabledStyle={style_disabled}
                >
                    {children}
                </Dropzone>
            </div>
        );
    }
}

Upload.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * The contents of the uploaded file as a binary string
     */
    contents: PropTypes.oneOfType([
        /**
         * If `multiple` is `false`, then the contents will be a string
         */
        PropTypes.string,

        /**
         * If `multiple` is `true`, then the contents will be a list of strings
         */
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * The name of the file(s) that was(were) uploaded.
     * Note that this does not include the path of the file
     * (for security reasons).
     */
    filename: PropTypes.oneOfType([
        /**
         * If `multiple` is `false`, then the contents will be a string
         */
        PropTypes.string,

        /**
         * If `multiple` is `true`, then the contents will be a list of strings
         */
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * The last modified date of the file that was uploaded in unix time
     * (seconds since 1970).
     */
    last_modified: PropTypes.oneOfType([
        /**
         * If `multiple` is `false`, then the contents will be a number
         */
        PropTypes.number,

        /**
         * If `multiple` is `true`, then the contents will be a list of numbers
         */
        PropTypes.arrayOf(PropTypes.number),
    ]),

    /**
     * Contents of the upload component
     */
    children: PropTypes.oneOfType([PropTypes.node, PropTypes.string]),

    /**
     * Allow specific types of files.
     * See https://github.com/okonet/attr-accept for more information.
     * Keep in mind that mime type determination is not reliable across
     * platforms. CSV files, for example, are reported as text/plain
     * under macOS but as application/vnd.ms-excel under Windows.
     * In some cases there might not be a mime type set at all.
     * See: https://github.com/react-dropzone/react-dropzone/issues/276
     */
    accept: PropTypes.string,

    /**
     * Enable/disable the upload component entirely
     */
    disabled: PropTypes.bool,

    /**
     * Disallow clicking on the component to open the file dialog
     */
    disable_click: PropTypes.bool,

    /**
     * Maximum file size. If `-1`, then infinite
     */
    max_size: PropTypes.number,

    /**
     * Minimum file size
     */
    min_size: PropTypes.number,

    /**
     * Allow dropping multiple files
     */
    multiple: PropTypes.bool,

    /**
     * HTML class name of the component
     */
    className: PropTypes.string,

    /**
     * HTML class name of the component while active
     */
    className_active: PropTypes.string,

    /**
     * HTML class name of the component if rejected
     */
    className_reject: PropTypes.string,

    /**
     * HTML class name of the component if disabled
     */
    className_disabled: PropTypes.string,

    /**
     * CSS styles to apply
     */
    style: PropTypes.object,

    /**
     * CSS styles to apply while active
     */
    style_active: PropTypes.object,

    /**
     * CSS styles if rejected
     */
    style_reject: PropTypes.object,

    /**
     * CSS styles if disabled
     */
    style_disabled: PropTypes.object,

    /**
     * Dash-supplied function for updating props
     */
    setProps: PropTypes.func,

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

Upload.defaultProps = {
    disabled: false,
    disable_click: false,
    max_size: -1,
    min_size: 0,
    multiple: false,
    style: {},
    style_active: {
        borderStyle: 'solid',
        borderColor: '#6c6',
        backgroundColor: '#eee',
    },
    style_disabled: {
        opacity: 0.5,
    },
    style_reject: {
        borderStyle: 'solid',
        borderColor: '#c66',
        backgroundColor: '#eee',
    },
};
