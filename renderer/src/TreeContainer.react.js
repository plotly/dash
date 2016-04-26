import HTML5Backend from 'react-dnd-html5-backend';
import { DragDropContext } from 'react-dnd';
import { connect } from 'react-redux'

import renderTree from './renderTree.js';

const UnconnectedContainer = props => renderTree(
    props.layout.toJS(),
    props.dependencyGraph,
    props.paths
);

const Container = connect(
    state => ({      // map state to props
        layout: state.layout,
        dependencyGraph: state.dependencyGraph,
        paths: state.paths
    })
)(UnconnectedContainer);

export default DragDropContext(HTML5Backend)(Container);
