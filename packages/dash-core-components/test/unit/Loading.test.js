import Loading from '../../src/components/Loading.react.js';
import React from 'react';
import {render} from 'enzyme';

test('Loading renders', () => {
    const statusMock = {
        is_loading: true,
        prop_name: 'children',
        component_name: 'div',
    };
    const loading = render(
        <Loading loading_state={statusMock}>
            <div>Loading is done!</div>
        </Loading>
    );

    expect(loading.html()).toMatchSnapshot('Loading with is_loading=true');
});
test('Loading renders without loading_state', () => {
    const loading = render(
        <Loading>
            <div>Loading is done!</div>
        </Loading>
    );

    expect(loading.html()).toEqual('<div>Loading is done!</div>');
});
test('Loading renders without loading_state.is_loading', () => {
    const statusMock = {
        prop_name: 'children',
        component_name: 'div',
    };
    const loading = render(
        <Loading loading_state={statusMock}>
            <div>Loading is done!</div>
        </Loading>
    );

    expect(loading.html()).toEqual('<div>Loading is done!</div>');
});
test('Loading renders without prop_name', () => {
    const statusMock = {
        is_loading: true,
        component_name: 'div',
    };
    const loading = render(
        <Loading loading_state={statusMock}>
            <div>Loading is done!</div>
        </Loading>
    );

    expect(loading.html()).toMatchSnapshot('Loading with is_loading=true');
});
test('Loading renders without loading_state.component_name', () => {
    const statusMock = {
        is_loading: true,
        prop_name: 'children',
    };
    const loading = render(
        <Loading loading_state={statusMock}>
            <div>Loading is done!</div>
        </Loading>
    );

    expect(loading.html()).toMatchSnapshot('Loading with is_loading=true');
});
test('Loading renders with multiple children', () => {
    const statusMock = {
        is_loading: true,
        prop_name: 'children',
        component_name: 'div',
    };
    const loading = render(
        <Loading loading_state={statusMock}>
            <div>Child 1</div>
            <div>Child 2</div>
            <div>Child 3</div>
        </Loading>
    );

    expect(loading.html()).toMatchSnapshot('Loading with is_loading=true');
});

test("Loading checks all it's children for a loading_state", () => {
    const statusMock = {
        is_loading: true,
        prop_name: 'children',
        component_name: 'div',
    };
    const loading = render(
        <Loading>
            <div>Child 1</div>
            <div>Child 2</div>
            <div loading_state={statusMock}>Child 3</div>
        </Loading>
    );

    expect(loading.html()).toMatchSnapshot('Loading spinner for children');
});
