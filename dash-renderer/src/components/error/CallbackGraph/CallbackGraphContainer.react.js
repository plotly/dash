import React, {useState, useMemo, useEffect} from 'react';
import PropTypes from 'prop-types';
import Cytoscape from 'cytoscape';
import CytoscapeComponent from 'react-cytoscapejs';
import ReactJson from 'react-json-view'

import './CallbackGraphContainer.css';
import stylesheet from './CallbackGraphContainerStylesheet';
import {
  getEdgeTypes,
  updateSelectedNode,
  updateChangedProps,
  updateCallback
} from './CallbackGraphEffects';

// Set the layout method.
// NOTE: dagre should be nicer for DAG, but even with manual
//       cycle pruning, it gives terrible results with State.
const cyLayout = {
  name: 'breadthfirst',
  directed: true,
  padding: 20,
  grid: true,
  spacingFactor: 0.5
};

/**
 * Generates all the elements (nodes, edeges) for the dependency graph.
 */
function generateElements(dependenciesRequest, profile) {

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
      elements.push({data: {id: child, label: `${property}`, parent: parent, type: 'property'}});
    }

  }

  function recordEdge([sourceId, sourceProperty], [targetId, targetProperty], type, label) {
    const source = `${sourceId}.${sourceProperty}`;
    const target = `${targetId}.${targetProperty}`;
    elements.push({data: {
      source: source,
      target: target,
      type: type,
      label: label || ''
    }});
  }

  dependenciesRequest.content.map((callback, i) => {

      const cb = ['__dash_callback__', callback.output];
      const cbProfile = profile.callbacks[callback.output] || {};
      const count = cbProfile.callCount || 0;
      const time = cbProfile.totalTime || 0;

      elements.push({data: {
        id: `${cb[0]}.${cb[1]}`,
        label: `callback.${i}`,
        type: 'callback',
        lang: callback.clientside_function ? 'javascript' : 'python',
        count: count,
        time: count > 0 ? Math.round(time/count) : 0,
        loadingSet: Date.now(),
        errorSet: Date.now()
      }});

      callback.output.replace(/^\.\./, '')
                     .replace(/\.\.$/, '')
                     .split('...')
                     .forEach(o => {
                       const node = o.split('.');
                       recordNode(node);
                       recordEdge(cb, node, 'output');
                     });

      callback.inputs.map(({id, property}) => {
        const node = [id, property];
        recordNode(node);
        recordEdge(node, cb, 'input');
      });

      callback.state.map(({id, property}) => {
        const node = [id, property];
        recordNode(node);
        recordEdge(node, cb, 'state');
      });

  });

  return elements;

}

function CallbackGraphContainer(props) {

  const {paths, layout, changed, profile, dependenciesRequest} = props;
  const [selected, setSelected] = useState(null);
  const [cytoscape, setCytoscape] = useState(null);

  // Generate and memoize the elements.
  const elements = useMemo(
    () => generateElements(dependenciesRequest, profile),
    [dependenciesRequest]
  );

  // Custom hook to make sure cytoscape is loaded.
  const useCytoscapeEffect = (effect, condition) => {
    useEffect(() => {if (cytoscape) return effect(cytoscape)}, condition)
  };

  // Adds callbacks once cyctoscape is intialized.
  useCytoscapeEffect((cy) => {
    cytoscape.on('tap', 'node', e => setSelected(e.target));
    cytoscape.on('tap', e => { if (e.target === cy) setSelected(null); });
  }, [cytoscape]);

  // Set node classes on selected.
  useCytoscapeEffect((cy) => {
    if (selected) return updateSelectedNode(cy, selected.data().id);
  }, [selected]);

  // Flash classes when props change. Uses changed as a trigger. Also
  // flash all input edges originating from this node and highlight
  // the subtree that contains the selected node.
  useCytoscapeEffect((cy) => {
    if (changed) return updateChangedProps(cy, changed.id, changed.props)
  }, [changed]);

  // Update callbacks from profiling information.
  useCytoscapeEffect((cy) => profile.updated.forEach(cb => (
    updateCallback(cy, cb, profile.callbacks[cb])
  )), [profile.updated]);

  // FIXME: Move to a new component?
  // Generate the element introspection data.
  let elementName = '';
  let elementInfo = {};

  if (selected) {

    function getComponent(id) {
      return paths[id].reduce((o, key) => o[key], layout)
    }

    function getPropValue(data) {
      const parent = getComponent(data.parent);
      return parent ? parent.props[data.label] : undefined;
    }

    const reducer = (o, e) => ({ ...o, [e.data().id]: getPropValue(e.data())});
    const data = selected.data();

    switch(data.type) {

      case 'component': {
        const {id, ...rest} = getComponent(data.id).props;
        elementInfo = rest;
        elementName = data.id;
        break;
      }

      case 'property': {
        elementName = data.parent;
        elementInfo[data.label] = getPropValue(data);
        break;
      }

      case 'callback': {
        elementName = data.label;
        elementInfo.language = data.lang;

        // Remove uid and set profile. Note: len('__dash_callback__.') = 18
        const {uid, ...rest} = profile.callbacks[data.id.slice(18)];
        const edges = getEdgeTypes(selected);

        elementInfo.profile = rest;
        elementInfo.inputs = edges.input.sources().reduce(reducer, {});
        elementInfo.states = edges.state.sources().reduce(reducer, {});
        elementInfo.outputs = edges.output.targets().reduce(reducer, {});

        break;
      }

    }

  }

  // We now have all the elements. Render.
  return (
      <div className="dash-callback-dag--container">
        <CytoscapeComponent
          style={{width: '100%', height: '100%'}}
          cy={setCytoscape}
          elements={elements}
          layout={cyLayout}
          stylesheet={stylesheet}
        />
      { selected ?
        <div className="dash-callback-dag--info">
          <ReactJson
            src={elementInfo}
            name={elementName}
            iconStyle="triangle"
            displayDataTypes={false}
            displayObjectSize={false}
          />
        </div>
        : null
      }
      </div>

  );

}

CallbackGraphContainer.propTypes = {
    paths: PropTypes.object,
    layout: PropTypes.object,
    changed: PropTypes.object,
    profile: PropTypes.object,
    dependenciesRequest: PropTypes.object,
};

export {CallbackGraphContainer};
