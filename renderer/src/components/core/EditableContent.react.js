import React, { PropTypes } from 'react';

import { connect } from 'react-redux'
import { editChildrenString } from '../../actions'

/*
 * EditableContent passes a connected onChange handler down to its child
 * as a prop
 */

const mapStateToProps = (state, ownProps) => {
  return {}
}

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onChange: (e) => {
      dispatch(editChildrenString(e.target.value, ownProps.path))
    }
  }
}

const EditableContent = ({ onChange, children }) => {
    // pass onChange as props to the child element e.g. an <input>
    return React.cloneElement(children, { onChange });
};

EditableContent.propTypes = {
    onChange: PropTypes.func.isRequired
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(EditableContent);
