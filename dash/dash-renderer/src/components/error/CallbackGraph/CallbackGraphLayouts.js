const forceLayout = {
    name: 'fcose',
    padding: 100,
    animate: false
};

const dagreLayout = {
    name: 'dagre',
    padding: 100,
    ranker: 'tight-tree',
    nodeDimensionsIncludeLabels: true
};

export const layouts = {
    'top-down': {...dagreLayout, spacingFactor: 0.8},
    'left-right': {...dagreLayout, nodeSep: 0, rankSep: 80, rankDir: 'LR'},
    force: forceLayout,
    'force-loose': forceLayout
};
