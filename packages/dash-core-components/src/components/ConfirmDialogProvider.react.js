import React from 'react';
import PropTypes from 'prop-types';

import ConfirmDialog from './ConfirmDialog.react'



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
        const { id, setProps, children } = this.props;

        // Will lose the previous onClick of the child
        const wrapClick = (child) => React.cloneElement(child, {onClick: () =>
            {
                setProps({
                    displayed: true
                });
            }
        });

        const realChild = children.props
            ? children.props.children
            : children.map(e => e.props.children);

        return (
            <div id={id}>
                {
                    realChild && realChild.length
                        ? realChild.map(wrapClick)
                        : wrapClick(realChild)
                }
                <ConfirmDialog {...this.props}/>
            </div>
        )
    }
}

ConfirmDialogProvider.defaultProps = {
    submit_n_clicks: 0,
    submit_n_clicks_timestamp: -1,
    cancel_n_clicks: 0,
    cancel_n_clicks_timestamp: -1
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
    children: PropTypes.any
};
