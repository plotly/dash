import {DepGraph} from 'dependency-graph';
import {append, keys, merge} from 'ramda';

const initialStateGraph = new DepGraph();
const initialEventGraph = new DepGraph();
const initialGraph = {
    StateGraph: initialStateGraph,
    EventGraph: initialEventGraph
};

function computeGraph(dependencies, graph, graphType) {
    return function(observerId) {
        // Add observers to the graph
        if(!graph.hasNode(observerId)) {
            graph.addNode(observerId, {});
        }

        /*
         * Add controllers to the graph with their data.
         * data is either `state` or `event`.
         * - `state`, which describes which props this controller
         *            should include
         * - `event`, which describes which events this controller
         *            should respond to
         */
        dependencies[observerId][graphType].forEach(
            function addStateNodes(controller) {
                if(!graph.hasNode(controller.id)) {
                    graph.addNode(controller.id, {[observerId]: []});
                }
                graph.addDependency(observerId, controller.id);
                /*
                 * A controller may be observed by several components
                 * and each component may depend on different props or events
                 *
                 * {
                 *      inputComponentId: {
                 *          observerComponentId1: ['value', 'style'],
                 *          observerComponentId2: ['className'],
                 *      }
                 * }
                 */
                const existingControllerData = graph.getNodeData(controller.id)[observerId]
                const newControllerData = controller[
                    graphType === 'state' ? 'prop' : 'event'
                ];
                const controllerData = append(
                    newControllerData,
                    existingControllerData
                );
                const allControllerData = merge(
                    graph.getNodeData(controller.id),
                    {[observerId]: controllerData}
                );
                graph.setNodeData(controller.id, allControllerData);
            }
        );
    }
}

const graphs = (state = initialGraph, action) => {
    switch (action.type) {
        case 'COMPUTE_GRAPHS': {
            const dependencies = action.payload;
            const stateGraph = new DepGraph();
            const eventGraph = new DepGraph();

            // add ID's to all the components
            keys(dependencies).forEach(computeGraph(dependencies, stateGraph, 'state'));
            keys(dependencies).forEach(computeGraph(dependencies, eventGraph, 'events'));

            return {StateGraph: stateGraph, EventGraph: eventGraph};

        }

        default:
            return state;

    }
}

export default graphs;
