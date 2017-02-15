import { connect } from 'react-redux'
import { isEmpty } from 'ramda'
import React, {PropTypes} from 'react';
import renderTree from './renderTree';


const UnconnectedContainer = props => {
    // TODO: Request status? Loading, error, ...
    if (isEmpty(props.layout)) {
        return (<div>loading...</div>);
    }
    return renderTree(
        props.layout,
        props.dependencyGraph
    );
}

UnconnectedContainer.propTypes = {
    layout: PropTypes.object,
    dependencyGraph: PropTypes.object
};

const Container = connect(
    // map state to props
    state => ({
        layout: state.layout,
        paths: state.paths
    })
)(UnconnectedContainer);

export default Container;
