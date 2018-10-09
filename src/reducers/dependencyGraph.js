import {DepGraph} from 'dependency-graph';

const initialGraph = {};

const graphs = (state = initialGraph, action) => {
    switch (action.type) {
        case 'COMPUTE_GRAPHS': {
            const dependencies = action.payload;
            const inputGraph = new DepGraph();
            const eventGraph = new DepGraph();

            dependencies.forEach(function registerDependency(dependency) {
                const {output, inputs, events} = dependency;
                const outputId = `${output.id}.${output.property}`;
                inputs.forEach(inputObject => {
                    const inputId = `${inputObject.id}.${inputObject.property}`;
                    inputGraph.addNode(outputId);
                    inputGraph.addNode(inputId);
                    inputGraph.addDependency(inputId, outputId);
                });
                events.forEach(eventObject => {
                    const eventId = `${eventObject.id}.${eventObject.event}`;
                    eventGraph.addNode(outputId);
                    eventGraph.addNode(eventId);
                    eventGraph.addDependency(eventId, outputId);
                });
            });

            return {InputGraph: inputGraph, EventGraph: eventGraph};
        }

        default:
            return state;
    }
};

export default graphs;
