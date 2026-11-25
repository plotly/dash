import PlotlyGraph from '../../../src/fragments/Graph.react';

function setup() {
    const figure = {
        data: [{y: [1, 2, 3]}],
        layout: {title: {text: 'original'}},
    };
    const props = {id: 'graph', figure, setProps: jest.fn()};
    const graph = new PlotlyGraph(props);
    const events: Record<string, (data: object) => void> = {};
    const gd = {
        layout: {...figure.layout} as Record<string, object>,
        on: (name: string, handler: (data: object) => void) => {
            events[name] = handler;
        },
    };
    Object.assign(graph.gd, {current: gd});
    graph.plot = jest.fn(() => Promise.resolve());
    graph.amendTraces = jest.fn(promise => promise);
    graph.bindEvents();
    const relayout = (key: string, value: object) => {
        gd.layout[key] = value;
        events.plotly_relayout({[key]: value});
        return props.setProps.mock.calls
            .filter(([update]) => update.figure)
            .pop()[0].figure;
    };
    const receive = (figure = graph.props.figure) => {
        const nextProps = {...graph.props, figure};
        // eslint-disable-next-line new-cap
        graph.UNSAFE_componentWillReceiveProps(nextProps);
        Object.assign(graph, {props: nextProps});
    };
    return {figure, graph, props, relayout, receive};
}

describe('relayout figure synchronization', () => {
    it('keeps changes from consecutive events before props arrive', () => {
        const {figure, relayout} = setup();
        relayout('yaxis', {range: [0, 5]});
        const synced = relayout('xaxis', {range: [0, 1]});
        expect(synced.layout.yaxis.range).toEqual([0, 5]);
        expect(synced.layout.xaxis.range).toEqual([0, 1]);
        expect(synced.data).toBe(figure.data);
        expect(figure.layout).toEqual({title: {text: 'original'}});
    });

    it('retains pending changes through unrelated prop updates', () => {
        const {relayout, receive} = setup();
        relayout('yaxis', {range: [0, 5]});
        receive();
        const synced = relayout('xaxis', {range: [0, 1]});
        expect(synced.layout.yaxis.range).toEqual([0, 5]);
    });

    it('retains later changes when an earlier sync is acknowledged', () => {
        const {relayout, receive} = setup();
        const first = relayout('yaxis', {range: [0, 5]});
        relayout('xaxis', {range: [0, 1]});
        receive(first);
        const synced = relayout('title', {text: 'updated'});
        expect(synced.layout.yaxis.range).toEqual([0, 5]);
        expect(synced.layout.xaxis.range).toEqual([0, 1]);
    });

    it('uses an external figure as the base for subsequent events', () => {
        const {relayout, receive} = setup();
        relayout('yaxis', {range: [0, 5]});
        const external = {
            data: [{y: [5, 4, 3]}],
            layout: {title: {text: 'external'}},
        };
        receive(external);
        const synced = relayout('xaxis', {range: [0, 1]});
        expect(synced.data).toBe(external.data);
        expect(synced.layout.title.text).toBe('external');
        expect(synced.layout.yaxis).toBeUndefined();
    });
});
