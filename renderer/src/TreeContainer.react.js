// import HTML5Backend from 'react-dnd-html5-backend';
// import { DragDropContext } from 'react-dnd';
import React from 'react';
import { connect } from 'react-redux'

import renderTree from './renderTree';

const UnconnectedContainer = props => {
    // TODO: Request status? Loading, error, ...
    if (props.layout.isEmpty()) {
        return (<div>loading...</div>);
    }
    return renderTree(
        props.layout.toJS(),
        props.dependencyGraph
    );
}

const Container = connect(
    state => ({      // map state to props
        layout: state.layout,
        dependencyGraph: state.dependencyGraph,
        paths: state.paths
    })
)(UnconnectedContainer);

export default Container;
// export default DragDropContext(HTML5Backend)(Container);
