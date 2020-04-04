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
      'width': 2,
      'label': 'data(label)',
      'line-color': '#888888',
      'target-arrow-color': '#888888',
      'target-arrow-shape': 'triangle',
      'target-arrow-fill': 'filled',
      'arrow-scale': 1,
      "curve-style": "bezier",
      "control-point-step-size": 40
    }
  },

  {
    selector: 'edge[type="state"]',
    style: {
      'line-style': 'dashed'
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
    selector: 'node[type="callback"]',
    style: {
      'width': 20,
      'height': 20,
      'shape': 'ellipse',
    }
  },

  {
    selector: 'node[type="callback"][lang="javascript"]',
    style: {
      'content': 'JS',
      'color': '#323330',
      'background-color': '#F0DB4F'
    }
  },

  {
    selector: 'node[type="callback"][lang="python"]',
    style: {
      'content': 'PY',
      'color': '#323330',
      'background-color': '#00CC96'
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
  },

  {
    selector: '.selectedNode',
    style: {
      'ghost': 'yes',
      'ghost-offset-x': 2,
      'ghost-offset-y': 2,
      'ghost-opacity': 0.25,
      'border-width': 2,
      'border-style': 'solid',
      'border-color': '#888888'
    }
  },

];

export default stylesheet;
