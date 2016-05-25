import HTML5Backend from 'react-dnd-html5-backend';
import { DragDropContext } from 'react-dnd';
import { connect } from 'react-redux'

import renderTree from './renderTree.js';

const UnconnectedContainer = props => renderTree(props.layout.toJS());

const Container = connect(
    state => ({layout: state.layout}) // map state to props
)(UnconnectedContainer);

export default DragDropContext(HTML5Backend)(Container);
