import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { isEmpty } from 'ramda';


export default class GlobalErrorOverlay extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const { resolve, visible, error } = this.props;
    return (
      <div>
        <div>{this.props.children}</div>
        <div style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          height: '300px',
          width: '400px',
          overflowY: 'auto',
          display: visible
        }}>
          {isEmpty(error.backEnd) ? null : (
            <button onClick={() => resolve('backEnd')}>
              Resolve BackEnd Error
            </button>
          )}
          <ul>
            {error.frontEnd.map((e) => (<li>
              <h3>{e.error.name}</h3>
              <p>{e.error.message}</p>
              <button onClick={() => resolve('frontEnd', e.myUID)}>
                Resolve Error
              </button>
              {e.error.stack.split('\n').map((line) => (<p>{line}</p>))}
            </li>))}
          </ul>
        </div>
      </div>
    )
  }
}

GlobalErrorOverlay.propTypes = {
    children: PropTypes.object,
    resolve: PropTypes.func,
    visible: PropTypes.bool,
    error: PropTypes.object
}
