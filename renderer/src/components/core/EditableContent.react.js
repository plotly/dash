import React, { PropTypes } from 'react';

import { connect } from 'react-redux'
import { updateProps } from '../../actions'

/*
 * EditableContent passes a connected onChange handler down to its child
 * as a prop
 */

const mapStateToProps = (state, ownProps) => {
  return {}
}

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    updateProps: (newProps) => {
        console.warn('newProps: ', newProps);
        dispatch(updateProps({
            props: newProps,
            itempath: React.Children.only(ownProps.children).props.path
        }));
    }
  }
}

const EditableContent = ({ updateProps, children }) => {
    // pass onChange as props to the child element e.g. an <input>
    return React.cloneElement(children, {updateProps});
};

EditableContent.propTypes = {
    onChange: PropTypes.func.isRequired
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(EditableContent);
