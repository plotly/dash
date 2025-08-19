import React from 'react';
import PropTypes from 'prop-types';

import ConfirmDialog from './ConfirmDialog.react';
import LoadingElement from '../utils/LoadingElement';

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
    render() {
        const {displayed, id, setProps, children} = this.props;

        // Will lose the previous onClick of the child
        const wrapClick = child =>
            React.cloneElement(child, {
                onClick: () => setProps({displayed: true}),
            });

        return (
            <LoadingElement id={id}>
                {Array.isArray(children)
                    ? children.map(wrapClick)
                    : wrapClick(children)}
                <ConfirmDialog {...this.props} displayed={displayed} />
            </LoadingElement>
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
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
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
};
