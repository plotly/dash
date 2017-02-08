import { connect } from 'react-redux'
import { isEmpty } from 'ramda'
import React from 'react';
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

const Container = connect(
    // map state to props
    state => ({
        layout: state.layout,
        dependencyGraph: state.dependencyGraph,
        paths: state.paths
    })
)(UnconnectedContainer);

export default Container;
