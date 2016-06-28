import React, {PropTypes} from 'react';

import { connect } from 'react-redux'
import { updateProps } from '../../actions'

/*
 * EditableContent passes a connected updateProps handler down to its child
 * as a prop
 */

/* eslint-disable no-unused-vars */
const mapStateToProps = (state, ownProps) => {
    return {}
}
/* eslint-enable no-unused-vars */

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        valueChanged: (newProps) => {
            console.warn('newProps: ', newProps); // eslint-disable-line
            dispatch(updateProps({
                props: newProps,
                itempath: React.Children.only(ownProps.children).props.path
            }));
        }
    }
}

const EditableContent = ({valueChanged, children}) => {
    // pass `valueChanged` handler as prop to the child element e.g. an <input>
    return React.cloneElement(children, {valueChanged});
};

EditableContent.propTypes = {
    valueChanged: PropTypes.func.isRequired
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(EditableContent);
