import React, {Component} from 'react';
import './CallbackGraphContainer.css';

import Cytoscape from 'cytoscape';
import Dagre from 'cytoscape-dagre';
import CytoscapeComponent from 'react-cytoscapejs';
Cytoscape.use(Dagre);

import PropTypes from 'prop-types';

const stylesheet = [

  {
    selector: '*',
    style: {
      'font-size': 12,
      'font-family': '"Arial", sans-serif',
    }
  },

  {
    selector: 'edge',
    style: {
      'width': 1,
      'label': 'data(label)',
      'line-color': '#888888',
      'target-arrow-color': '#888888',
      'target-arrow-shape': 'triangle',
      'target-arrow-fill': 'filled',
      'arrow-scale': 1,
      'curve-style': 'bezier'
    }
  },

  {
    selector: 'node',
    style: {
      'color': '#333333',
      'padding': 6,
      'text-valign': 'center',
      'text-halign': 'center',
    }
  },

  {
    selector: 'node[type="clientside-callback"], node[type="serverside-callback"]',
    style: {
      'width': 20,
      'height': 20,
      'shape': 'ellipse',
    }
  },

  {
    selector: 'node[type="clientside-callback"]',
    style: {
      'content': 'PY',
      'color': '#00CC96',
      'background-color': '#F0DB4F'
    }
  },

  {
    selector: 'node[type="serverside-callback"]',
    style: {
      'content': 'JS',
      'color': '#323330',
      'background-color': '#F0DB4F'
    }
  },

  {
    selector: 'node[type="component"]',
    style: {
      'width': 'label',
      'height': 'label',
      'shape': 'rectangle',
      'content': 'data(label)',
      'text-valign': 'top',
      'background-color': '#B9C2CE'
    }
  },

  {
    selector: 'node[type="property"]',
    style: {
      'width': 'label',
      'height': 20,
      'shape': 'rectangle',
      'content': 'data(label)',
      'color': 'white',
      'background-color': '#109DFF'
    }
  }

];

class CallbackGraphContainer extends Component {

    render() {

      const {dependenciesRequest} = this.props;

      // Generate all the elements.
      const consumed = [];
      const elements = [];

      function recordNode([id, property]) {
        const parent = `${id}`;
        const child = `${id}.${property}`;

        if (!consumed.includes(parent)) {
          consumed.push(parent);
          elements.push({data: {id: parent, label: parent, type: 'component'}});
        }

        if (!consumed.includes(child)) {
          consumed.push(child);
          elements.push({data: {id: child, label: child, parent: parent, type: 'property'}});
        }

      }

      function recordEdge([sourceId, sourceProperty], [targetId, targetProperty], label) {
        const source = `${sourceId}.${sourceProperty}`;
        const target = `${targetId}.${targetProperty}`;
        elements.push({data: {source: source, target: target, label: label || ''}});
      }

      dependenciesRequest.content.map((callback, i) => {

          const cb = ['callback', i];
          const cbLabel = `callback.${i}`;
          elements.push({data: {
            id: cbLabel,
            label: cbLabel,
            type: callback.clientside_function ? 'serverside-callback' : 'clientside-callback'
          }});

          callback.output.replace(/^\.\./, '')
                         .replace(/\.\.$/, '')
                         .split('...')
                         .forEach(o => {
                           const node = o.split('.');
                           recordNode(node);
                           recordEdge(cb, node);
                         });

          callback.inputs.map(({id, property}) => {
            const node = [id, property];
            recordNode(node);
            recordEdge(node, cb);
          });

      });

      // Create the layout.
      const layout = {
        name: 'dagre'
      };
      console.log(dependenciesRequest.content);

      // We now have all the elements. Render.
      return (
          <CytoscapeComponent
            className="dash-callback-dag--container"
            elements={elements}
            layout={layout}
            stylesheet={stylesheet}
          />
      );

    }

}

CallbackGraphContainer.propTypes = {
    dependenciesRequest: PropTypes.object,
};

export {CallbackGraphContainer};
