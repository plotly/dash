import React, { PropTypes } from 'react';
import { connect } from 'react-redux';

import { notifyObservers, updateProps } from '../../actions';

/*
 * NotifyObservers passes a connected notifyObservers handler down to
 * its child as a prop
 */

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        notifyObservers: (updatedProps) => {
            const payload = {
                updatedProps, // pass in the entire prop object or just updates?

                // we *need* the ID, should we just pass / merge everything in?
                id: React.Children.only(ownProps.children).props.id,
                itempath: React.Children.only(ownProps.children).props.path
            };

            // Update this component's props
            dispatch(updateProps(payload));

            // Update this component's observers with the updated props
            dispatch(notifyObservers(payload));

        }
    }
};

const NotifyObservers = ({ notifyObservers, children }) => {
    // pass notifyObservers as props to the child element e.g. an <input>
    return React.cloneElement(children, {notifyObservers});
}

NotifyObservers.propTypes = {
    notifyObservers: PropTypes.func.isRequired
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(NotifyObservers);
