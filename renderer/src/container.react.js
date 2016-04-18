/*eslint-env browser */

'use strict';

import React, { Component } from 'react';
import HTML5Backend from 'react-dnd-html5-backend';
import { DragDropContext } from 'react-dnd';

import renderTree from './renderTree.js';
import spec from './spec.js';

// const store = createStore(reducer);

class Container extends Component {
  render () {
      return renderTree(spec);
    //   return (
    //       <Provider store={store}>
    //         {renderTree(spec)}
    //     </Provider>
    // );
  }
}

export default DragDropContext(HTML5Backend)(Container);
