import React, {Component, PropTypes} from 'react';
import Plotly from 'plotly.js';

export default class PlotlyGraph extends Component {
    _plot(){
        const {id, data, layout} = this.props;

        Plotly.newPlot(id, data, layout);
    }

    // "Invoked once, only on the client (not on the server),
    // immediately after the initial rendering occurs."
    componentDidMount() {
        this._plot();
    }

    shouldComponentUpdate(nextProps) {
        // TODO optimize this check
        const dataChanged = JSON.stringify(this.props.data) !== JSON.stringify(nextProps.data)
        if (dataChanged) return true;

        const layoutChanged = JSON.stringify(this.props.layout) !== JSON.stringify(nextProps.layout);
        return layoutChanged;
    }

    // "Invoked immediately after the component's updates are flushed to the DOM.
    // This method is not called for the initial render."
    componentDidUpdate() {
        this._plot();
    }

    render(){
        const {width, height, id} = this.props
        const style = {width, height};

        return (
            <div
                id={id}
                style={style}
            />
        );
    }
}

PlotlyGraph.propTypes = {
    /**
     * Plotly `figure.data` array. See schema:
     * https://api.plot.ly/v2/plot-schema?sha1=
     */
    data: PropTypes.array,

    /**
     * Plotly `figure.layout` object. See schema:
     * https://api.plot.ly/v2/plot-schema?sha1=
     */
    layout: PropTypes.object,

    /**
     * Height of graph, e.g. '600px' or '100%'
     */
    height: PropTypes.string,

    /**
     * Width of graph, e.g. '600px' or '100%'
     */
    width: PropTypes.string
}

PlotlyGraph.defaultProps = {
    data: [],
    layout: {},
    height: '600px',
    width: '100%'
};
