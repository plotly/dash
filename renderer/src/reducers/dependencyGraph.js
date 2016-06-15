import {DepGraph} from 'dependency-graph';

import {crawlLayout} from './utils';

const initialGraph = new DepGraph();

const dependencyGraph = (state = initialGraph, action) => {
    switch (action.type) {
        case 'COMPUTE_GRAPH': {
            const layout = action.payload;
            const graph = new DepGraph();

            // add ID's to all the components
            crawlLayout(layout, child => {
                if (child.props && child.props.id) {
                    graph.addNode(child.props.id);
                }
            });

            // add dependencies to the graph
            crawlLayout(layout, child => {
                if (child.dependencies) {
                    for (let i = 0; i < child.dependencies.length; i++) {
                        graph.addDependency(
                            child.props.id,
                            child.dependencies[i]
                        );
                    }
                }
            });
            return graph;
        }

        default:
            return state;
    }
}

export default dependencyGraph;
