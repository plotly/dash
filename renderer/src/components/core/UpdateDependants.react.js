import React, { PropTypes } from 'react';
import { connect } from 'react-redux';

import { updateDependants, updateProps } from '../../actions';

/*
 * UpdateDependants passes a connected updateDependants handler down to
 * its child as a prop
 */

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        updateDependants: (updatedProps) => {
            const payload = {
                updatedProps, // pass in the entire prop object or just updates?

                // we *need* the ID, should we just pass / merge everything in?
                id: React.Children.only(ownProps.children).props.id,
                itempath: React.Children.only(ownProps.children).props.path
            };

            // Update this component's props
            dispatch(updateProps(payload));

            // Update this component's dependants depending in these new props
            dispatch(updateDependants(payload));

        }
    }
};

const UpdateDependants = ({ updateDependants, children }) => {
    // pass updateDependants as props to the child element e.g. an <input>
    return React.cloneElement(children, {updateDependants});
}

UpdateDependants.propTypes = {
    updateDependants: PropTypes.func.isRequired
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(UpdateDependants);
