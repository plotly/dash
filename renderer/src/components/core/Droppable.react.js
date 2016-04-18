'use strict';

import React, { PropTypes, Component } from 'react';
import { DropTarget } from 'react-dnd';

const spec = {
    drop(props, monitor, component) {return {}},
    hover(props, monitor, component) {return {}},
    canDrop(props, monitor) {return true;}
};

function collectProps(connect, monitor) {
    return {
        connectDropTarget: connect.dropTarget(),
        isOver: monitor.isOver(),
        isOverCurrent: monitor.isOver({ shallow: true }),
        canDrop: monitor.canDrop(),
        itemType: monitor.getItemType()
    };
}

class Droppable extends Component {
    render() {
        console.warn('Droppable: ', this.props);
        const { canDrop, isOver, connectDropTarget } = this.props;
        const isActive = canDrop && isOver;

        const style = {
            borderWidth: '1px',
            borderStyle: isActive ? 'solid' : (canDrop ? 'dashed' : 'none'),
            borderColor: 'blue'
        };

        return connectDropTarget(
            <div style={style}>
                {this.props.children}
            </div>
        );
    }
}

export default DropTarget('Draggable', spec, collectProps)(Droppable);
