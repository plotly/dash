import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';

import { AppMode, AppFlavor } from 'demo/AppMode';

describe(`filter special characters`, () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.ColumnsInSpace}`);
        DashTable.toggleScroll(false);
    });

    it('can filter on special column id', () => {
        DashTable.clickFilterInputById('b+bb');
        DashTable.focusedType(`Wet${Key.Enter}`);

        DashTable.clickFilterInputById('c cc');
        DashTable.focusedType(`gt 90${Key.Enter}`);

        DashTable.clickFilterInputById('d:dd');
        DashTable.focusedType(`lt 12500${Key.Enter}`);

        DashTable.clickFilterInputById('e-ee');
        DashTable.focusedType(`is prime${Key.Enter}`);

        DashTable.clickFilterInputById('f_ff');
        DashTable.focusedType(`le 106${Key.Enter}`);

        DashTable.clickFilterInputById('g.gg');
        DashTable.focusedType(`gt 1000${Key.Enter}`);
        DashTable.clickFilterInputById('b+bb');

        DashTable.getCellById(0, 'rows').within(() => cy.get('.dash-cell-value').should('have.html', '101'));
        DashTable.getCellById(1, 'rows').should('not.exist');
        DashTable.getFilterInputById('b+bb').should('have.value', 'Wet');
        DashTable.getFilterInputById('c cc').should('have.value', 'gt 90');
        DashTable.getFilterInputById('d:dd').should('have.value', 'lt 12500');
        DashTable.getFilterInputById('e-ee').should('have.value', 'is prime');
        DashTable.getFilterInputById('f_ff').should('have.value', 'le 106');
        DashTable.getFilterInputById('g.gg').should('have.value', 'gt 1000');
    });
});

describe('filter', () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Default}&flavor=${AppFlavor.FilterNative}`);
        DashTable.toggleScroll(false);
    });

    it('handles hovering onto other filtering cells', () => {
        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType(`gt 100`);
        DashTable.clickFilterInputById('ddd');
        DashTable.focusedType('lt 20000');

        DashTable.getCellById(0, 'eee').trigger('mouseover', { force: true });

        DashTable.getFilterInputById('ccc').should('have.value', 'gt 100');
        DashTable.getFilterInputById('ddd').should('have.value', 'lt 20000');
    });

    it('handles invalid queries', () => {
        let cell_0;
        let cell_1;

        DashTable.getCellById(0, 'ccc')
            .within(() => cy.get('.dash-cell-value')
                .then($el => cell_0 = $el[0].innerHTML));

        DashTable.getCellById(1, 'ccc')
            .within(() => cy.get('.dash-cell-value')
                .then($el => cell_1 = $el[0].innerHTML));

        DashTable.clickFilterInputById('ddd');
        DashTable.focusedType('"20 a000');
        DashTable.clickFilterInputById('eee');
        DashTable.focusedType('is prime2');
        DashTable.clickFilterInputById('bbb');
        DashTable.focusedType('! !"');
        DashTable.clickFilterInputById('ccc');

        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_0));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_1));

        DashTable.getFilterInputById('bbb').should('have.value', '! !"');
        DashTable.getFilterInputById('ddd').should('have.value', '"20 a000');
        DashTable.getFilterInputById('eee').should('have.value', 'is prime2');

        DashTable.getFilterById('bbb').should('have.class', 'invalid');
        DashTable.getFilterById('ddd').should('have.class', 'invalid');
        DashTable.getFilterById('eee').should('have.class', 'invalid');
    });

    it('filters `Text` columns with `contains` without operator', () => {
        DashTable.clickFilterInputById('bbb');
        DashTable.focusedType('Tr');
        DashTable.clickFilterInputById('ccc');

        DashTable.getFilterInputById('bbb').should('have.value', 'Tr');
        DashTable.getCellById(0, 'bbb-readonly').within(() => cy.get('.dash-cell-value').should('have.html', 'label: Tropical Beaches'));
    });

    it('filters `Numeric` columns with `equal` without operator', () => {
        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType('100');
        DashTable.clickFilterInputById('bbb');

        DashTable.getFilterInputById('ccc').should('have.value', '100');
        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '100'));
    });

    it('does not use text-based relational operators unless they are followed by a space', () => {
        DashTable.clickCellById(2, 'ccc');
        DashTable.focusedType(`le5${Key.Enter}`);

        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType(`le5${Key.Enter}`);
        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', 'le5'));
        DashTable.getCellById(0, 'rows').within(() => cy.get('.dash-cell-value').should('have.html', '3'));

        cy.get('.clear-filters').click();

        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType(`le 5${Key.Enter}`);
        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '1'));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '2'));
        DashTable.getCellById(2, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '4'));
        DashTable.getCellById(3, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '5'));
    });

    it('uses symbol relational operators that are not followed by a space', () => {
        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType(`<=5${Key.Enter}`);
        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '1'));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '2'));
        DashTable.getCellById(2, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '3'));
        DashTable.getCellById(3, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '4'));
        DashTable.getCellById(4, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '5'));
    });

    it('typing invalid followed by valid query fragment does not reset invalid', () => {
        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType(`is prime2`);
        DashTable.clickFilterInputById('ddd');
        DashTable.focusedType('lt 20000');
        DashTable.clickFilterInputById('eee');

        DashTable.getFilterInputById('ccc').should('have.value', 'is prime2');
        DashTable.getFilterInputById('ddd').should('have.value', 'lt 20000');
    });

    it('reset updates results and filter fields', () => {
        let cell_0;
        let cell_1;

        DashTable.getCellById(0, 'ccc')
            .within(() => cy.get('.dash-cell-value')
                .then($el => cell_0 = $el[0].innerHTML));

        DashTable.getCellById(1, 'ccc')
            .within(() => cy.get('.dash-cell-value')
                .then($el => cell_1 = $el[0].innerHTML));

        DashTable.clickFilterInputById('ccc');
        DashTable.focusedType(`gt 100`);
        DashTable.clickFilterInputById('ddd');
        DashTable.focusedType('lt 20000');
        DashTable.clickFilterInputById('eee');
        DashTable.focusedType('is prime');
        DashTable.clickFilterInputById('bbb');
        DashTable.focusedType(`Wet`);
        DashTable.clickFilterInputById('ccc');

        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '101'));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '109'));

        DashTable.getFilterInputById('bbb').should('have.value', 'Wet');
        DashTable.getFilterInputById('ccc').should('have.value', 'gt 100');
        DashTable.getFilterInputById('ddd').should('have.value', 'lt 20000');
        DashTable.getFilterInputById('eee').should('have.value', 'is prime');

        cy.get('.clear-filters').click();

        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_0));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_1));

        DashTable.getFilterInputById('bbb').should('have.value', '');
        DashTable.getFilterInputById('ccc').should('have.value', '');
        DashTable.getFilterInputById('ddd').should('have.value', '');
        DashTable.getFilterInputById('eee').should('have.value', '');
    });
});