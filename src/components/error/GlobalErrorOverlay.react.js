import React, { Component } from 'react';
import PropTypes from 'prop-types';


const styles = {
  root: {
    position: 'relative',
  },
  overlay: {
    position: 'relative',
    backgroundColor: 'rgb(255, 0, 0, .2)',
    display: 'inline-block',
    height: '100vh',
    width: '100vw',
    padding: 0,
    margin: -8
  },
  childWrapper: {
    position: 'relative',
    zIndex: -1
  }
}

export default class GlobalErrorOverlay extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const { resolve } = this.props;
    return (
      <div style={styles.root}>
        <div
          style={styles.overlay}>
          <div style={styles.childWrapper}>{this.props.children}</div>
          <button onClick={resolve}>Resolve Error</button>
        </div>
      </div>
    )
  }
}

GlobalErrorOverlay.propTypes = {
    children: PropTypes.object,
    resolve: PropTypes.func
}
