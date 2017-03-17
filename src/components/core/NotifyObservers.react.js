import {connect} from 'react-redux';
import {isEmpty} from 'ramda';
import {notifyObservers, updateProps} from '../../actions';
import React, {PropTypes} from 'react';

/*
 * NotifyObservers passes a connected `setProps` handler down to
 * its child as a prop
 */

function mapStateToProps (state) {
    return {graphs: state.graphs, paths: state.paths};
}

function mapDispatchToProps (dispatch) {
    return {dispatch};
}

function mergeProps(stateProps, dispatchProps, ownProps) {
    const {dispatch} = dispatchProps;

    return {
        id: ownProps.id,
        children: ownProps.children,

        EventGraph: stateProps.graphs.EventGraph,
        StateGraph: stateProps.graphs.StateGraph,

        fireEvent: function fireEvent({event}) {
            // Update this component's observers with the updated props
            dispatch(notifyObservers({event, id: ownProps.id}));
        },

        setProps: function setProps(newProps) {
            const payload = {
                props: newProps,
                id: ownProps.id,
                itempath: stateProps.paths[ownProps.id]
            };

            // Update this component's props
            dispatch(updateProps(payload));

            // Fire an event that the props have changed.
            // TODO - Will updateProps have finished by the time this is fired?
            // TODO - Add support for subscribing to a particular prop change?
            dispatch(notifyObservers({event: 'propChange', id: ownProps.id}));
        }
    }

}

function NotifyObserversComponent ({
    children,
    id,

    EventGraph,
    StateGraph,

    fireEvent,
    setProps
}) {

    // TODO - Check if it triggers this particular event
    const thisComponentTriggersEvents = (
        EventGraph.hasNode(id) && EventGraph.dependantsOf(id).length
    );
    const thisComponentSharesState = (
        StateGraph.hasNode(id) && StateGraph.dependantsOf(id).length
    );
    const extraProps = {};
    if (thisComponentSharesState) {
        extraProps.setProps = setProps;
    }
    if (thisComponentTriggersEvents) {
        extraProps.fireEvent = fireEvent;
    }

    if (!isEmpty(extraProps)) {
        return React.cloneElement(children, extraProps);
    } else {
        return children;
    }
}

NotifyObserversComponent.propTypes = {
    id: PropTypes.string.isRequired,
    children: PropTypes.node.isRequired,
    path: PropTypes.array.isRequired
};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
)(NotifyObserversComponent);
