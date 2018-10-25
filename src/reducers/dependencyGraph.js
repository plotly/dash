import {DepGraph} from 'dependency-graph';

const initialGraph = {};

const graphs = (state = initialGraph, action) => {
    switch (action.type) {
        case 'COMPUTE_GRAPHS': {
            const dependencies = action.payload;
            const inputGraph = new DepGraph();

            dependencies.forEach(function registerDependency(dependency) {
                const {output, inputs} = dependency;
                inputs.forEach(inputObject => {
                    const inputId = `${inputObject.id}.${inputObject.property}`;
                    inputGraph.addNode(output);
                    inputGraph.addNode(inputId);
                    inputGraph.addDependency(inputId, output);
                });
            });

            return {InputGraph: inputGraph};
        }

        default:
            return state;
    }
};

export default graphs;
