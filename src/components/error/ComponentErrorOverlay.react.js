import React, { Component } from 'react';
import PropTypes from 'prop-types';


const styles = {
  root: {
    position: 'relative'
  },
  overlay: {
    position: 'relative',
    padding: '2px',
    backgroundColor: 'rgb(255, 0, 0, .5)',
    border: '1px solid black',
    borderRadius: '2px',
    display: 'inline-block'
  },
  childWrapper: {
    position: 'relative',
    zIndex: -1
  },
  popOverOpen: {'display': 'inline'},
  popOverClosed: {'display': 'none'}
}

export default class ComponentErrorOverlay extends Component {
  constructor(props) {
    super(props);
    this.state = {
      popoverOpen: false
    }
    this.togglePopOver = this.togglePopOver.bind(this);
  }

  togglePopOver() {
    this.setState({
      popoverOpen: !this.state.popoverOpen
    });
  }

  render() {
    const { error, componentId, componentType, resolve } = this.props;
    const errorLocationString = "Error in " + componentType + '(id=' + componentId + ')';
    const errorString = error.name + " -- " + error.message;
    return (
      <div style={styles.root}>
        <div
          onClick={this.togglePopOver}
          style={styles.overlay}>
          <div style={styles.childWrapper}>
            <p>Error!</p>
          </div>
          <div
            style={this.state.popoverOpen ? styles.popOverOpen : styles.popOverClosed}
            toggle={this.togglePopOver}
          >
            <strong>{errorLocationString}</strong>
            <p>{errorString}</p>
            <button onClick={resolve}>Resolve Error</button>
          </div>
        </div>
      </div>
    )
  }
}

ComponentErrorOverlay.propTypes = {
    children: PropTypes.object,
    oldChildren: PropTypes.object,
    error: PropTypes.object,
    componentId: PropTypes.string,
    componentType: PropTypes.string,
    resolve: PropTypes.func
}
