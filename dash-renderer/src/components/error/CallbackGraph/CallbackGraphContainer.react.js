import React, {useState, useMemo, useEffect} from 'react';
import './CallbackGraphContainer.css';
import stylesheet from './CallbackGraphContainerStylesheet';

import ReactJson from 'react-json-view'

import Cytoscape from 'cytoscape';
import Dagre from 'cytoscape-dagre';
import CytoscapeComponent from 'react-cytoscapejs';
Cytoscape.use(Dagre);

import PropTypes from 'prop-types';


/**
 * Generates all the elements (nodes, edeges) for the dependency graph.
 */
function generateElements(dependenciesRequest) {

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

      const cb = ['callback', i];
      const cbLabel = `callback.${i}`;
      elements.push({data: {
        id: cbLabel,
        label: cbLabel,
        type: 'callback',
        lang: callback.clientside_function ? 'javascript' : 'python'
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

  const {paths, layout, dependenciesRequest} = props;
  const [selected, setSelected] = useState(null);
  const [cytoscape, setCytoscape] = useState(null);

  // Adds callbacks once cyctoscape is intialized.
  useEffect(() => {
    if (cytoscape) {

      // Select / deselect nodes.
      cytoscape.on('tap', 'node', e => setSelected(e.target));
      cytoscape.on('tap', e => {
        if (e.target === cytoscape)
          setSelected(null);
      })

    }
  }, [cytoscape]);

  // Set node classes on selected.
  useEffect(() => {
    if (cytoscape && selected) {
      cytoscape.center(selected);
      selected.addClass("selectedNode");
      return () => selected.removeClass("selectedNode");
    }
  }, [selected]);

  // Generate and memoize the elements.
  const elements = useMemo(
    () => generateElements(dependenciesRequest),
    [dependenciesRequest]
  );

  // Set the layout method.
  const cyLayout = {
    name: 'dagre'
  };

  // Generate the element introspection data.
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

      case 'component':
        const {id, ...rest} = getComponent(data.id).props;
        elementInfo = rest;
        break;

      case 'property':
        elementInfo.value = getPropValue(data);
        break;

      case 'callback':
        elementInfo.language = data.lang;

        elementInfo.inputs = cytoscape.filter(`[target = "${data.id}"]`)
                                     .sources()
                                     .reduce(reducer, {});

        elementInfo.outputs = cytoscape.filter(`[source = "${data.id}"]`)
                                      .targets()
                                      .reduce(reducer, {});
        break;

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
            name={selected.data().id}
            iconStyle="triangle"
            displayDataTypes={false}
            displayObjectSize={false}
            src={elementInfo}
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
    dependenciesRequest: PropTypes.object,
};

export {CallbackGraphContainer};
