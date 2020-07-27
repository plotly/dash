import React, {useState, useMemo, useEffect} from 'react';
import {useSelector} from 'react-redux'
import CytoscapeComponent from 'react-cytoscapejs';
import JSONTree from 'react-json-tree'
import {omit, path} from 'ramda';

import {getPath} from '../../../actions/paths';
import {stringifyId} from '../../../actions/dependencies';

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

/*
 * Generates all the elements (nodes, edeges) for the dependency graph.
 */
function generateElements(graphs, profile) {

  const consumed = [];
  const elements = [];

  function recordNode(id, property) {

    const idStr = stringifyId(id);
    const idType = typeof id === 'object' ? 'wildcard' : 'component';

    const parent = idStr;
    const child = `${idStr}.${property}`;

    if (!consumed.includes(parent)) {
      consumed.push(parent);
      elements.push({data: {
        id: idStr,
        label: idStr,
        type: idType
      }});
    }

    if (!consumed.includes(child)) {
      consumed.push(child);
      elements.push({data: {
        id: child,
        label: property,
        parent: parent,
        type: 'property'
      }});
    }

    return child;

  }

  function recordEdge(source, target, type) {
    elements.push({data: {
      source: source,
      target: target,
      type: type
    }});
  }

  graphs.callbacks.map((callback, i) => {

      const cb = `__dash_callback__.${callback.output}`;
      const cbProfile = profile.callbacks[callback.output] || {};
      const count = cbProfile.callCount || 0;
      const time = cbProfile.totalTime || 0;

      elements.push({data: {
        id: cb,
        label: `callback.${i}`,
        type: 'callback',
        lang: callback.clientside_function ? 'javascript' : 'python',
        count: count,
        time: count > 0 ? Math.round(time/count) : 0,
        loadingSet: Date.now(),
        errorSet: Date.now()
      }});

      callback.outputs.map(({id, property}) => {
        const node = recordNode(id, property);
        recordEdge(cb, node, 'output');
      });

      callback.inputs.map(({id, property}) => {
        const node = recordNode(id, property);
        recordEdge(node, cb, 'input');
      });

      callback.state.map(({id, property}) => {
        const node = recordNode(id, property);
        recordEdge(node, cb, 'state');
      });

  });

  console.log(elements)
  return elements;

}

// len('__dash_callback__.')
const cbPrefixLen = 18;

function CallbackGraphContainer() {

  // Grab items from the redux store.
  const paths = useSelector(state => state.paths);
  const layout = useSelector(state => state.layout);
  const graphs = useSelector(state => state.graphs);
  const profile = useSelector(state => state.profile);
  const changed = useSelector(state => state.changed);

  console.log(paths, layout, graphs, profile);

  // Keep track of cytoscape reference and user selected items.
  const [selected, setSelected] = useState(null);
  const [cytoscape, setCytoscape] = useState(null);

  // Generate and memoize the elements.
  const elements = useMemo(
    () => generateElements(graphs, profile),
    [graphs]
  );

  // Custom hook to make sure cytoscape is loaded.
  const useCytoscapeEffect = (effect, condition) => {
    useEffect(() => {if (cytoscape) { effect(cytoscape); } }, condition)
  };

  // Adds callbacks once cyctoscape is intialized.
  useCytoscapeEffect((cy) => {
    cytoscape.on('tap', 'node', e => setSelected(e.target));
    cytoscape.on('tap', e => { if (e.target === cy) { setSelected(null); } });
  }, [cytoscape]);

  // Set node classes on selected.
  useCytoscapeEffect((cy) => {
    if (selected) { updateSelectedNode(cy, selected.data().id); }
  }, [selected]);

  // Flash classes when props change. Uses changed as a trigger. Also
  // flash all input edges originating from this node and highlight
  // the subtree that contains the selected node.
  useCytoscapeEffect((cy) => {
    if (changed) { updateChangedProps(cy, changed.id, changed.props); }
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
      return path(getPath(paths, id), layout);
    }

    function getPropValue(data) {
      const parent = getComponent(data.parent);
      return parent ? parent.props[data.label] : undefined;
    }

    const reducer = (o, e) => ({ ...o, [e.data().id]: getPropValue(e.data())});
    const data = selected.data();

    switch(data.type) {

      case 'component': {
        const rest = omit(['id'], getComponent(data.id).props);
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

        // Remove uid and set profile.
        const callbackOutputId = data.id.slice(cbPrefixLen);
        if (profile.callbacks.hasOwnProperty(callbackOutputId)) {
          elementInfo.profile = omit(['uid'], profile.callbacks[callbackOutputId]);
        } else {
          elementInfo.profile = {};
        }

        const edges = getEdgeTypes(selected);
        elementInfo.inputs = edges.input.sources().reduce(reducer, {});
        elementInfo.states = edges.state.sources().reduce(reducer, {});
        elementInfo.outputs = edges.output.targets().reduce(reducer, {});

        break;
      }

      default:
        console.log(data.type);
    }

  }

  // We now have all the elements. Render.
  return (
      <div className="dash-callback-dag--container">
        <CytoscapeComponent
          style={{width: '100%', height: '100%'}}
          cy={setCytoscape}
          elements={elements}
          layout={window.layout || cyLayout}
          stylesheet={stylesheet}
        />
      { selected ?
        <div className="dash-callback-dag--info">
          <JSONTree
            data={elementInfo}
            theme="summerfruit"
            labelRenderer={(keys) => (
              keys.length === 1 ? elementName : keys[0]
            )}
            getItemString={(type, data, itemType) => (
              <span>{itemType}</span>
            )}
            shouldExpandNode={(keyName, data, level) => level <= 1}
          />
        </div>
        : null
      }
      </div>

  );

}

CallbackGraphContainer.propTypes = {};

export {CallbackGraphContainer};
