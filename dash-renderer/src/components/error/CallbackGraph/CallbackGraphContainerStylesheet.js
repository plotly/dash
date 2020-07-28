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
      "control-point-step-size": 40,
      'transition-property': 'line-color, target-arrow-color',
      'transition-duration': '0.25s',
      'transition-timing-function': 'ease-in-out-sine'
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
      'border-width': 2,
      'border-opacity': 0,
      'border-style': 'solid',
      'border-color': '#888888',
      'transition-property': 'border-opacity',
      'transition-duration': '0.25s',
      'transition-timing-function': 'ease-in-out-sine'
    }
  },

  {
    selector: 'node[type="callback"]',
    style: {
      'width': 20,
      'height': 20,
      'shape': 'ellipse',
      'label': e => `${e.data().count}\n${e.data().time} ms`,
      'font-size': 8,
      'text-wrap': 'wrap',
      'text-justification': 'center',
    }
  },

  {
    selector: 'node[type="callback"][lang="javascript"]',
    style: {
      // 'content': 'JS',
      'color': '#323330',
      'background-color': '#F0DB4F'
    }
  },

  {
    selector: 'node[type="callback"][lang="python"]',
    style: {
      // 'content': 'PY',
      'color': '#323330',
      'background-color': '#00CC96'
    }
  },

  {
    selector: 'node[type="component"], node[type="wildcard"]',
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
    selector: 'node[type="wildcard"]',
    style: {
      'shape': 'rectangle',
      'label': 'data(label)',
      'text-valign': 'center',
      'text-halign': 'right',
      'text-wrap': 'wrap',
      'text-justification': 'left',
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
    selector: '.selected-node',
    style: {
      'ghost': 'yes',
      'ghost-offset-x': 2,
      'ghost-offset-y': 2,
      'ghost-opacity': 0.25,
      'border-opacity': 1,
    }
  },

  {
    selector: '.prop-changed, .callback-loading',
    style: {
      'border-color': '#CC43B7',
      'border-width': 2,
      'border-opacity': 1,
    }
  },

  {
    selector: '.callback-error',
    style: {
      'background-color': '#E1332E',
    }
  },

  {
    selector: '.triggered',
    style: {
      'line-color': '#CC43B7',
      'target-arrow-color': '#CC43B7'
    }
  },

  {
    selector: '.inactive',
    style: {
      'opacity': 0.5
    }
  }


];

export default stylesheet;
