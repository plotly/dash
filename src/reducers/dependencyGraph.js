import {type} from 'ramda';
import {DepGraph} from 'dependency-graph';

const initialGraph = {};

const graphs = (state = initialGraph, action) => {
    switch (action.type) {
        case 'COMPUTE_GRAPHS': {
            const dependencies = action.payload;
            const inputGraph = new DepGraph();

            dependencies.forEach(function registerDependency(dependency) {
                const {output, inputs} = dependency;

                // Multi output supported will be a string already
                // Backward compatibility by detecting object.
                const outputId = type(output) === 'Object' ?
                    `${output.id}.${output.property}` : output;
                inputs.forEach(inputObject => {
                    const inputId = `${inputObject.id}.${inputObject.property}`;
                    inputGraph.addNode(outputId);
                    inputGraph.addNode(inputId);
                    inputGraph.addDependency(inputId, outputId);
                });
            });

            return {InputGraph: inputGraph};
        }

        default:
            return state;
    }
};

export default graphs;
