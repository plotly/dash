import React, {PropTypes} from 'react';
import { connect } from 'react-redux';

import { notifyObservers, updateProps } from '../../actions';

/*
 * NotifyObservers passes a connected `valueChanged` handler down to
 * its child as a prop
 */

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        valueChanged: (newProps, event='default') => {
            const payload = {
                // we *need* the ID, should we just pass / merge everything in?
                id: React.Children.only(ownProps.children).props.id,
                // TODO pass in the entire prop object or just updates?
                props: newProps,
                itempath: React.Children.only(ownProps.children).props.path
            };

            // Update this component's props
            dispatch(updateProps(payload));

            // Update this component's observers with the updated props
            dispatch(notifyObservers(payload, event));

        }
    }
};

const NotifyObservers = ({ valueChanged, children }) => {
    // pass `valueChanged` handler as prop to the child element e.g. an <input>
    return React.cloneElement(children, {valueChanged});
}

NotifyObservers.propTypes = {
    valueChanged: PropTypes.func.isRequired
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(NotifyObservers);
