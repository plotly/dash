import React, {Component} from 'react'; // eslint-disable-line no-unused-vars
import PropTypes from 'prop-types';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faCopy, faCheckCircle} from '@fortawesome/free-regular-svg-icons';

const clipboardAPI = navigator.clipboard;

function wait(ms) {
    return new Promise(r => setTimeout(r, ms));
}

/**
 * The Clipboard component copies text to the clipboard
 */

export default class Clipboard extends React.Component {
    constructor(props) {
        super(props);
        this.copyToClipboard = this.copyToClipboard.bind(this);
        this.copySuccess = this.copySuccess.bind(this);
        this.getTargetText = this.getTargetText.bind(this);
        this.loading = this.loading.bind(this);
        this.stringifyId = this.stringifyId.bind(this);
        this.state = {
            copied: false,
        };
    }

    // stringifies object ids used in pattern matching callbacks
    stringifyId(id) {
        if (typeof id !== 'object') {
            return id;
        }
        const stringifyVal = v => (v && v.wild) || JSON.stringify(v);
        const parts = Object.keys(id)
            .sort()
            .map(k => JSON.stringify(k) + ':' + stringifyVal(id[k]));
        return '{' + parts.join(',') + '}';
    }

    async copySuccess(content) {
        const showCopiedIcon = 1000;
        await clipboardAPI.writeText(content);
        this.setState({copied: true});
        await wait(showCopiedIcon);
        this.setState({copied: false});
    }

    getTargetText() {
        // get the inner text.  If none, use the content of the value param
        const id = this.stringifyId(this.props.target_id);
        const target = document.getElementById(id);
        if (!target) {
            throw new Error(
                'Clipboard copy failed: no element found for target_id ' +
                    this.props.target_id
            );
        }
        let content = target.innerText;
        if (!content) {
            content = target.value;
            content = content === undefined ? null : content;
        }
        return content;
    }

    async loading() {
        while (this.props.loading_state?.is_loading) {
            await wait(100);
        }
    }

    async copyToClipboard() {
        this.props.setProps({
            n_clicks: this.props.n_clicks + 1,
        });

        let content;
        if (this.props.target_id) {
            content = this.getTargetText();
        } else {
            await wait(100); // gives time for callback to start
            await this.loading();
            content = this.props.content;
        }
        if (content) {
            this.copySuccess(content);
        }
    }

    componentDidMount() {
        if (!clipboardAPI) {
            console.warn('Copy to clipboard not available with this browser'); // eslint-disable-line no-console
        }
    }

    render() {
        const {id, title, className, style, loading_state} = this.props;
        const copyIcon = <FontAwesomeIcon icon={faCopy} />;
        const copiedIcon = <FontAwesomeIcon icon={faCheckCircle} />;
        const btnIcon = this.state.copied ? copiedIcon : copyIcon;

        return clipboardAPI ? (
            <div
                id={id}
                title={title}
                style={style}
                className={className}
                onClick={this.copyToClipboard}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
            >
                <i> {btnIcon}</i>
            </div>
        ) : null;
    }
}

Clipboard.defaultProps = {
    content: null,
    target_id: null,
    n_clicks: 0,
};

Clipboard.propTypes = {
    /**
     * The ID used to identify this component.
     */
    id: PropTypes.string,

    /**
     * The id of target component containing text to copy to the clipboard.
     * The inner text of the `children` prop will be copied to the clipboard.  If none, then the text from the
     *  `value` prop will be copied.
     */
    target_id: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),

    /**
     * The text to  be copied to the clipboard if the `target_id` is None.
     */
    content: PropTypes.string,

    /**
     * The number of times copy button was clicked
     */
    n_clicks: PropTypes.number,

    /**
     * The text shown as a tooltip when hovering over the copy icon.
     */
    title: PropTypes.string,

    /**
     * The icon's styles
     */
    style: PropTypes.object,

    /**
     * The class  name of the icon element
     */
    className: PropTypes.string,

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

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,
};
