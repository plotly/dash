import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';

import {
    applyReloadState,
    recordReloadEdit,
    resetReloadState,
    shouldRecordReloadEdit,
    snapshotReloadState
} from '../src/reloadState';

const component = (id, props) => ({
    namespace: 'dash_core_components',
    type: 'Input',
    props: {id, ...props}
});

const layout = (aValue, bValue) => ({
    namespace: 'dash_html_components',
    type: 'Div',
    props: {
        children: [
            component('a', {value: aValue}),
            component('b', {value: bValue})
        ]
    }
});

const childValue = (lay, i) => lay.props.children[i].props.value;

describe('state preservation across hot reloads', () => {
    beforeEach(() => {
        resetReloadState();
        window.sessionStorage.clear();
    });

    it('restores a recorded UI edit when the initial value is unchanged', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        snapshotReloadState();

        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A1');
        // untouched component is left alone
        expect(childValue(out, 1)).to.equal('B0');
    });

    it('lets the new code win when the initial value changed', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        snapshotReloadState();

        const out = applyReloadState(layout('CHANGED', 'B0'));
        expect(childValue(out, 0)).to.equal('CHANGED');
    });

    it('keeps the first original value across repeated edits', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        recordReloadEdit(component('a', {value: 'A1'}), {value: 'A2'});
        snapshotReloadState();

        // the layout still starts at A0 - the latest edit is applied
        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A2');
    });

    it('applies each edit at most once', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        snapshotReloadState();

        applyReloadState(layout('A0', 'B0'));
        // e.g. a callback recreates the component later in the session
        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A0');
    });

    it('survives a fresh js context through sessionStorage', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        snapshotReloadState();

        // hard reload: module state is gone, sessionStorage remains
        resetReloadState();

        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A1');
    });

    it('consumes the sessionStorage snapshot on first apply', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        snapshotReloadState();
        applyReloadState(layout('A0', 'B0'));

        // manual browser refresh: fresh js context, no snapshot left
        resetReloadState();

        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A0');
    });

    it('keeps unmatched edits pending for later layout chunks', () => {
        recordReloadEdit(component('x', {value: 'X0'}), {value: 'X1'});
        snapshotReloadState();

        // initial layout doesn't contain x (e.g. pages content)
        applyReloadState(layout('A0', 'B0'));

        // a callback inserts it later
        const chunk = applyReloadState({
            props: {children: component('x', {value: 'X0'})}
        });
        expect(chunk.props.children.props.value).to.equal('X1');
    });

    it('preserves state again on a reload following a restore', () => {
        recordReloadEdit(component('a', {value: 'A0'}), {value: 'A1'});
        snapshotReloadState();
        applyReloadState(layout('A0', 'B0'));

        // second reload without touching the component again
        snapshotReloadState();
        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A1');
    });

    it('handles props that were not defined initially', () => {
        recordReloadEdit(component('a', {}), {value: 'A1'});
        snapshotReloadState();

        const out = applyReloadState(layout(undefined, 'B0'));
        expect(childValue(out, 0)).to.equal('A1');
    });

    it('ignores components without an id', () => {
        recordReloadEdit(
            {...component('a', {value: 'A0'}), props: {value: 'A0'}},
            {
                value: 'A1'
            }
        );
        snapshotReloadState();

        const out = applyReloadState(layout('A0', 'B0'));
        expect(childValue(out, 0)).to.equal('A0');
    });

    describe('shouldRecordReloadEdit', () => {
        const store = storage_type => ({
            namespace: 'dash_core_components',
            type: 'Store',
            props: {id: 's', ...(storage_type ? {storage_type} : {})}
        });

        const rt = renderType => ({renderType});

        it('records UI edits and clientside set_props on any component', () => {
            const c = component('a', {});
            expect(shouldRecordReloadEdit(c, rt('internal'))).to.equal(true);
            expect(shouldRecordReloadEdit(c, rt('clientsideApi'))).to.equal(
                true
            );
            expect(shouldRecordReloadEdit(c, rt('callback'))).to.equal(false);
            expect(shouldRecordReloadEdit(c, rt('websocket'))).to.equal(false);
            expect(shouldRecordReloadEdit(c, rt(undefined))).to.equal(false);
        });

        it('records server set_props flagged with recordState', () => {
            const c = component('a', {});
            expect(
                shouldRecordReloadEdit(c, {
                    renderType: 'callback',
                    recordState: true
                })
            ).to.equal(true);
            expect(
                shouldRecordReloadEdit(c, {
                    renderType: 'websocket',
                    recordState: true
                })
            ).to.equal(true);
        });

        it('records any write to a memory dcc.Store', () => {
            expect(
                shouldRecordReloadEdit(store('memory'), rt('callback'))
            ).to.equal(true);
            // memory is the default storage_type
            expect(shouldRecordReloadEdit(store(), rt('callback'))).to.equal(
                true
            );
            expect(shouldRecordReloadEdit(store(), rt('websocket'))).to.equal(
                true
            );
        });

        it('leaves local/session stores to their own persistence', () => {
            expect(
                shouldRecordReloadEdit(store('local'), rt('callback'))
            ).to.equal(false);
            expect(
                shouldRecordReloadEdit(store('session'), rt('callback'))
            ).to.equal(false);
        });
    });
});
