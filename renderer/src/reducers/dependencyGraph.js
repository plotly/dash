import {DepGraph} from 'dependency-graph';

import {crawlLayout} from './utils';
import spec from '../spec'; // TODO: this'll eventually load from the API

const initialGraph = new DepGraph();

// TODO: Don't initialize graph as side-effect of importing reducer.
// add ID's to all the components
crawlLayout(spec, child => {
    if (child.props && child.props.id) {
        initialGraph.addNode(child.props.id);
    }
});

// add dependencies to the graph
crawlLayout(spec, child => {
    if (child.dependencies) {
        for (let i = 0; i < child.dependencies.length; i++) {
            initialGraph.addDependency(child.props.id, child.dependencies[i]);
        }
    }
});

const dependencyGraph = (state = initialGraph, action) => {
    switch (action.type) {
        default:
            return state;
    }
}

export default dependencyGraph;
