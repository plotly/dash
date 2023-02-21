// padding needed for menubar / search-bar

const forceLayout = {
    name: 'fcose',
    padding: 100,
    animate: false
};

const dagreLayout = {
    name: 'dagre',
    padding: 10,
    ranker: 'tight-tree'

    /*     name: 'dagre',
    ranker: 'tight-tree',
    spacingFactor: 0.8,
    //fit should be only active when show only non 0?
    fit: true,
    padding:100,
    animation:false,
    nodeDimensionsIncludeLabels: true, */
};

export const layouts = {
    'top-down': {...dagreLayout, spacingFactor: 0.8},
    'left-right': {...dagreLayout, nodeSep: 0, rankSep: 80, rankDir: 'LR'},
    force: forceLayout,
    'force-loose': forceLayout
};
