import React, {Component, PropTypes} from 'react';
import Plotly from 'plotly.js';
import {contains, filter, map, type} from 'ramda';

const filterEventData = (eventData, event) => {
    let filteredEventData;
    if (contains(event, ['click', 'hover', 'selected'])) {
        filteredEventData = {
            /*
             * remove `data`, `layout`, `xaxis`, etc
             * objects from the event data since they're so big
             * and cause JSON stringify ciricular structure errors.
             */
            points: eventData.points = map(
                filter(function(o) {
                    return !contains(type(o), ['Object', 'Array'])
             }), eventData.points)
        }
    } else if (event === 'relayout') {
        /*
         * relayout shouldn't include any big objects
         * it will usually just contain the ranges of the axes like
         * "xaxis.range[0]": 0.7715822247381828,
         * "xaxis.range[1]": 3.0095292008680063`
         */
        filteredEventData = eventData;
    }
    return filteredEventData;
};

export default class PlotlyGraph extends Component {
    constructor(props) {
        super(props);
        this.bindEvents = this.bindEvents.bind(this);
        this.state = {hasPlotted: false};
    }

    plot(props) {
        const {id, figure, animate, animation_options} = props;
        const {hasPlotted} = this.state;
        const gd = document.getElementById(id);
        if (animate && hasPlotted && figure.data.length === gd.data.length) {
            return Plotly.animate(id, figure, animation_options);
        } else {
            return  Plotly.newPlot(id, figure).then(() => {
                this.bindEvents(props);
                this.setState({hasPlotted: true});
            });
        }
    }

    bindEvents(props) {
        const {id, fireEvent, valueChanged} = props;

        const gd = document.getElementById(id);

        gd.on('plotly_click', (eventData) => {
            const clickData = filterEventData(eventData, 'click');
            if (valueChanged) valueChanged({clickData});
            if (fireEvent) fireEvent({event: 'click'});
        });
        gd.on('plotly_hover', (eventData) => {
            const hoverData = filterEventData(eventData, 'hover');
            if (valueChanged) valueChanged({hoverData});
            if (fireEvent) fireEvent({event: 'hover'})
        });
        gd.on('plotly_selected', (eventData) => {
            const selectedData = filterEventData(eventData, 'selected');
            if (valueChanged) valueChanged({selectedData});
            if (fireEvent) fireEvent({event: 'selected'});
        });
        gd.on('plotly_relayout', (eventData) => {
            const relayoutData = filterEventData(eventData, 'relayout');
            if (valueChanged) valueChanged({relayoutData});
            if (fireEvent) fireEvent({event: 'relayout'});
        });
    }

    componentDidMount() {
        this.plot(this.props).then(() => {
            window.addEventListener('resize', () => {
                Plotly.Plots.resize(document.getElementById(this.props.id));
            });
        });
    }

    componentWillUnmount() {
        if (this.eventEmitter) {
            this.eventEmitter.removeAllListeners();
        }
    }

    shouldComponentUpdate(nextProps) {
        return (
            this.props.id !== nextProps.id ||
            JSON.stringify(this.props.style) !== JSON.stringify(nextProps.style)
        );
    }

    componentWillReceiveProps(nextProps) {
        const idChanged = this.props.id !== nextProps.id;
        if (idChanged) {
            /*
             * then the dom needs to get re-rendered with a new ID.
             * the graph will get updated in componentDidUpdate
             */
            return;
        }

        const figureChanged = this.props.figure !== nextProps.figure;

        /*
         * Rebind events in case fireEvent or valueChanged
         * wasn't defined on initial render
         * TODO - Is it safe to rebind events?
         */
        const shouldBindEvents = (
            (!this.props.valueChanged && nextProps.valueChanged) ||
            (!this.props.fireEvent && nextProps.fireEvent)
        );
        if (figureChanged) {
            this.plot(nextProps);
        } else if (shouldBindEvents) {
            this.bindEvents(nextProps);
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.id !== this.props.id) {
            this.plot(this.props);
        }
    }

    render(){
        const {style, id} = this.props;

        return (
            <div
                key={id}
                id={id}
                style={style}
            />
        );

    }
}

PlotlyGraph.propTypes = {
    /**
     * Data from latest click event
     */
    clickData: PropTypes.object,

    /**
     * Data from latest hover event
     */
    hoverData: PropTypes.object,

    /**
     * Data from latest select event
     */
    selectedData: PropTypes.object,

    /**
     * Data from latest zoom event
     */
    zoomData: PropTypes.object,

    /**
     * Plotly `figure` object. See schema:
     * https://plot.ly/javascript/reference
     */
    figure: PropTypes.object,

    /**
     * Generic style overrides on the plot div
     */
    style: PropTypes.object,

    /**
     * Beta: If true, animate between updates using
     * plotly.js's `animate` function
     */
    animate: PropTypes.bool,

    /**
     * Beta: Transition object containing animation settings.
     * Only applies if `animate` is `true`
     */
    transition: PropTypes.object,

    /**
     *
     */
    dashEvents: PropTypes.oneOf([
        'restyle',
        'relayout'
    ]),

    /**
     * Function that updates the state tree.
     */
    dashValueChanged: PropTypes.func,

    /**
     * Function that fires events
     */
    dashFireEvent: PropTypes.func
}

PlotlyGraph.defaultProps = {
    clickData: null,
    hoverData: null,
    selectedData: null,
    zoomData: null,
    figure: {data: [], layout: {}},
    animate: false,
    animation_options: {
        frame: {
            redraw: false
        },
        transition: {
            duration: 750,
            ease: 'cubic-in-out'
        }
    },
    layout: {}
};
