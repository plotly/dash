import {
    comparator,
    equals,
    forEach,
    has,
    isEmpty,
    lt,
    path,
    pathOr,
    sort
} from 'ramda';
import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import apiThunk from '../../actions/api';

class Reloader extends React.Component {
    constructor(props) {
        super(props);
        if (props.config.hot_reload) {
            const {interval, max_retry} = props.config.hot_reload;
            this.state = {
                interval,
                disabled: false,
                intervalId: null,
                packages: null,
                max_retry
            };
        } else {
            this.state = {
                disabled: true
            };
        }
        this._retry = 0;
        this._head = document.querySelector('head');
        this.clearInterval = this.clearInterval.bind(this);
    }

    clearInterval() {
        window.clearInterval(this.state.intervalId);
        this.setState({intervalId: null});
    }

    static getDerivedStateFromProps(props) {
        /*
         * Save the non-loading requests in the state in order to compare
         * current hashes with previous hashes.
         * Note that if there wasn't a "loading" state for the requests,
         * then we  could simply compare `props` with `prevProps` in
         * `componentDidUpdate`.
         */
        if (
            !isEmpty(props.reloadRequest) &&
            props.reloadRequest.status !== 'loading'
        ) {
            return {reloadRequest: props.reloadRequest};
        }
        return null;
    }

    componentDidUpdate(prevProps, prevState) {
        const {reloadRequest} = this.state;
        const {dispatch} = this.props;

        // In the beginning, reloadRequest won't be defined
        if (!reloadRequest) {
            return;
        }

        /*
         * When reloadRequest is first defined, prevState won't be defined
         * for one render loop.
         * The first reloadRequest defines the initial/baseline hash -
         * it doesn't require a reload
         */
        if (!has('reloadRequest', prevState)) {
            return;
        }

        if (
            reloadRequest.status === 200 &&
            path(['content', 'reloadHash'], reloadRequest) !==
                path(['reloadRequest', 'content', 'reloadHash'], prevState)
        ) {
            // Check for CSS (!content.hard) or new package assets
            if (
                reloadRequest.content.hard ||
                !equals(
                    reloadRequest.content.packages.length,
                    pathOr(
                        [],
                        ['reloadRequest', 'content', 'packages'],
                        prevState
                    ).length
                ) ||
                !equals(
                    sort(comparator(lt), reloadRequest.content.packages),
                    sort(
                        comparator(lt),
                        pathOr(
                            [],
                            ['reloadRequest', 'content', 'packages'],
                            prevState
                        )
                    )
                )
            ) {
                // Look if it was a css file.
                let was_css = false;
                // eslint-disable-next-line prefer-const
                for (let a of reloadRequest.content.files) {
                    if (a.is_css) {
                        was_css = true;
                        const nodesToDisable = [];

                        // Search for the old file by xpath.
                        const it = document.evaluate(
                            `//link[contains(@href, "${a.url}")]`,
                            this._head
                        );
                        let node = it.iterateNext();

                        while (node) {
                            nodesToDisable.push(node);
                            node = it.iterateNext();
                        }

                        forEach(
                            n => n.setAttribute('disabled', 'disabled'),
                            nodesToDisable
                        );

                        if (a.modified > 0) {
                            const link = document.createElement('link');
                            link.href = `${a.url}?m=${a.modified}`;
                            link.type = 'text/css';
                            link.rel = 'stylesheet';
                            this._head.appendChild(link);
                            // Else the file was deleted.
                        }
                    } else {
                        // If there's another kind of file here do a hard reload.
                        was_css = false;
                        break;
                    }
                }
                if (!was_css) {
                    // Assets file have changed
                    // or a component lib has been added/removed -
                    // Must do a hard reload
                    window.location.reload();
                }
            } else {
                // Backend code changed - can do a soft reload in place
                dispatch({type: 'RELOAD'});
            }
        } else if (
            this.state.intervalId !== null &&
            reloadRequest.status === 500
        ) {
            if (this._retry > this.state.max_retry) {
                this.clearInterval();
                // Integrate with dev tools ui?!
                window.alert(
                    `Hot reloading is disabled after failing ${this._retry} times. ` +
                        'Please check your application for errors, then refresh the page.'
                );
            }
            this._retry++;
        }
    }

    componentDidMount() {
        const {dispatch, reloadRequest} = this.props;
        const {disabled, interval} = this.state;
        if (!disabled && !this.state.intervalId) {
            const intervalId = window.setInterval(() => {
                // Prevent requests from piling up - reloading can take
                // many seconds (10-30) and the interval is 3s by default
                if (reloadRequest.status !== 'loading') {
                    dispatch(apiThunk('_reload-hash', 'GET', 'reloadRequest'));
                }
            }, interval);
            this.setState({intervalId});
        }
    }

    componentWillUnmount() {
        if (!this.state.disabled && this.state.intervalId) {
            this.clearInterval();
        }
    }

    render() {
        return null;
    }
}

Reloader.defaultProps = {};

Reloader.propTypes = {
    id: PropTypes.string,
    config: PropTypes.object,
    reloadRequest: PropTypes.object,
    dispatch: PropTypes.func,
    interval: PropTypes.number
};

export default connect(
    state => ({
        config: state.config,
        reloadRequest: state.reloadRequest
    }),
    dispatch => ({dispatch})
)(Reloader);
