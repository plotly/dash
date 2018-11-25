import React from 'react';
import PropTypes from 'prop-types';

const styles = {
  root: {
    position: 'relative'
  },
  overlay: {
    position: 'relative',
    padding: '2px',
    backgroundColor: 'rgb(0, 0, 255, .5)',
    border: '1px solid black',
    borderRadius: '2px',
    display: 'inline-block'
  },
  childWrapper: {
    position: 'relative',
    zIndex: -1
  }
}

function ComponentDisabledOverlay({ children }) {
  return (
    <div style={styles.root}>
      <div
        style={styles.overlay}>
        <div style={styles.childWrapper}>
          {children}
        </div>
      </div>
    </div>
  )
}

ComponentDisabledOverlay.propTypes = {
    children: PropTypes.object,
}

export default ComponentDisabledOverlay;
