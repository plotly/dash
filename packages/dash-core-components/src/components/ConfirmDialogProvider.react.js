import React from 'react';
import PropTypes from 'prop-types';

import ConfirmDialog from './ConfirmDialog.react';

/**
 * A wrapper component that will display a confirmation dialog
 * when its child component has been clicked on.
 *
 * For example:
 * ```
 * dcc.ConfirmDialogProvider(
 *     html.Button('click me', id='btn'),
 *     message='Danger - Are you sure you want to continue.'
 *     id='confirm')
 * ```
 */
export default class ConfirmDialogProvider extends React.Component {
    constructor(props) {
        super(props);
        this.state = {displayed: props.displayed};
    }

    componentWillReceiveProps(props) {
        this.setState({displayed: props.displayed});
    }

    render() {
        const {id, setProps, children, loading_state} = this.props;

        const displayed = this.state.displayed;

        // Will lose the previous onClick of the child
        const wrapClick = child =>
            React.cloneElement(child, {
                onClick: () => {
                    const update = {displayed: true};
                    this.setState(update);
                    if (setProps) {
                        setProps(update);
                    }
                },
            });

        const realChild = children.props
            ? children.props.children
            : children.map(e => e.props.children);

        return (
            <div
                id={id}
                data-dash-is-loading={loading_state && loading_state.is_loading}
            >
                {realChild && realChild.length
                    ? realChild.map(wrapClick)
                    : wrapClick(realChild)}
                <ConfirmDialog {...this.props} displayed={displayed} />
            </div>
        );
    }
}

ConfirmDialogProvider.defaultProps = {
    submit_n_clicks: 0,
    submit_n_clicks_timestamp: -1,
    cancel_n_clicks: 0,
    cancel_n_clicks_timestamp: -1,
};

ConfirmDialogProvider.propTypes = {
    id: PropTypes.string,

    /**
     * Message to show in the popup.
     */
    message: PropTypes.string,
    /**
     * Number of times the submit was clicked
     */
    submit_n_clicks: PropTypes.number,
    /**
     * Last time the submit button was clicked.
     */
    submit_n_clicks_timestamp: PropTypes.number,
    /**
     * Number of times the popup was canceled.
     */
    cancel_n_clicks: PropTypes.number,
    /**
     * Last time the cancel button was clicked.
     */
    cancel_n_clicks_timestamp: PropTypes.number,
    /**
     * Is the modal currently displayed.
     */
    displayed: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,
    /**
     * The children to hijack clicks from and display the popup.
     */
    children: PropTypes.any,

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
