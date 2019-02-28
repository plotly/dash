import {connect} from 'react-redux';
import {notifyObservers, updateProps} from '../../actions';
import React from 'react';
import PropTypes from 'prop-types';
import {isEmpty} from 'ramda';

/*
 * NotifyObservers passes a connected `setProps` handler down to
 * its child as a prop
 */

function mapStateToProps(state) {
    return {
        dependencies: state.dependenciesRequest.content,
        paths: state.paths,
    };
}

function mapDispatchToProps(dispatch) {
    return {dispatch};
}

function mergeProps(stateProps, dispatchProps, ownProps) {
    const {dispatch} = dispatchProps;
    return {
        id: ownProps.id,
        children: ownProps.children,
        dependencies: stateProps.dependencies,
        paths: stateProps.paths,
        loading_state: ownProps.loading_state,
        requestQueue: stateProps.requestQueue,

        setProps: function setProps(newProps) {
            const payload = {
                props: newProps,
                id: ownProps.id,
                itempath: stateProps.paths[ownProps.id],
            };

            // Update this component's props
            dispatch(updateProps(payload));

            // Update output components that depend on this input
            dispatch(notifyObservers({id: ownProps.id, props: newProps}));
        },
    };
}

function NotifyObserversComponent({
    children,
    id,
    paths,
    dependencies,
    setProps,
    loading_state,
}) {
    const thisComponentSharesState =
        dependencies &&
        dependencies.find(
            dependency =>
                dependency.inputs.find(input => input.id === id) ||
                dependency.state.find(state => state.id === id)
        );
    /*
     * Only pass in `setProps` if necessary.
     * This allows component authors to skip computing unneeded data
     * for `setProps`, which can be expensive.
     * For example, consider `hoverData` for graphs. If it isn't
     * actually used, then the component author can skip binding
     * the events for the component.
     *
     * TODO - A nice enhancement would be to pass in the actual
     * properties that are used into the component so that the
     * component author can check for something like
     * `subscribed_properties` instead of just `setProps`.
     */
    const extraProps = {};
    if (
        thisComponentSharesState &&
        // there is a bug with graphs right now where
        // the restyle listener gets assigned with a
        // setProps function that was created before
        // the item was added. only pass in setProps
        // if the item's path exists for now.
        paths[id]
    ) {
        extraProps.setProps = setProps;
    }

    if (children.props && !children.props.loading_state) {
        extraProps.loading_state = loading_state;
    }

    if (!isEmpty(extraProps)) {
        return React.cloneElement(children, extraProps);
    }
    return children;
}

NotifyObserversComponent.propTypes = {
    id: PropTypes.string.isRequired,
    children: PropTypes.node.isRequired,
    path: PropTypes.array.isRequired,
    loading_state: PropTypes.object,
};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
)(NotifyObserversComponent);
