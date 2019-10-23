import {type} from 'ramda';
import {DepGraph} from 'dependency-graph';
import {isMultiOutputProp, parseMultipleOutputs} from '../utils';

const initialGraph = {};

const graphs = (state = initialGraph, action) => {
    if (action.type === 'COMPUTE_GRAPHS') {
        const dependencies = action.payload;
        const inputGraph = new DepGraph();
        const multiGraph = new DepGraph();

        dependencies.forEach(function registerDependency(dependency) {
            const {output, inputs} = dependency;

            // Multi output supported will be a string already
            // Backward compatibility by detecting object.
            let outputId;
            if (type(output) === 'Object') {
                outputId = `${output.id}.${output.property}`;
            } else {
                outputId = output;
                if (isMultiOutputProp(output)) {
                    parseMultipleOutputs(output).forEach(out => {
                        multiGraph.addNode(out);
                        inputs.forEach(i => {
                            const inputId = `${i.id}.${i.property}`;
                            if (!multiGraph.hasNode(inputId)) {
                                multiGraph.addNode(inputId);
                            }
                            multiGraph.addDependency(inputId, out);
                        });
                    });
                } else {
                    multiGraph.addNode(output);
                    inputs.forEach(i => {
                        const inputId = `${i.id}.${i.property}`;
                        if (!multiGraph.hasNode(inputId)) {
                            multiGraph.addNode(inputId);
                        }
                        multiGraph.addDependency(inputId, output);
                    });
                }
            }

            inputs.forEach(inputObject => {
                const inputId = `${inputObject.id}.${inputObject.property}`;
                inputGraph.addNode(outputId);
                if (!inputGraph.hasNode(inputId)) {
                    inputGraph.addNode(inputId);
                }
                inputGraph.addDependency(inputId, outputId);
            });
        });

        return {InputGraph: inputGraph, MultiGraph: multiGraph};
    }

    return state;
};

export default graphs;
