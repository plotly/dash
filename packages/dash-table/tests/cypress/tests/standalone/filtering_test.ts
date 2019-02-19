import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

describe(`filter`, () => {
    describe(`special characters`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.ColumnsInSpace}`);
            DashTable.toggleScroll(false);
        });

        it('can filter on special column id', () => {
            DashTable.getFilterById('c cc').click();
            DOM.focused.type(`gt num(90)${Key.Enter}`);

            DashTable.getFilterById('d:dd').click();
            DOM.focused.type(`lt num(12500)${Key.Enter}`);

            DashTable.getFilterById('e-ee').click();
            DOM.focused.type(`is prime${Key.Enter}`);

            DashTable.getFilterById('f_ff').click();
            DOM.focused.type(`le num(106)${Key.Enter}`);

            DashTable.getFilterById('g.gg').click();
            DOM.focused.type(`gt num(1000)${Key.Enter}`);

            DashTable.getFilterById('b+bb').click();
            DOM.focused.type(`eq "Wet"${Key.Enter}`);

            DashTable.getCellById(0, 'rows').within(() => cy.get('.dash-cell-value').should('have.html', '101'));
            DashTable.getCellById(1, 'rows').should('not.exist');
        });
    });

    describe('reset', () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Filtering}`);
            DashTable.toggleScroll(false);
        });

        it('updates results and filter fields', () => {
            let cell_0;
            let cell_1;

            DashTable.getCellById(0, 'ccc')
                .within(() => cy.get('.dash-cell-value')
                    .then($el => cell_0 = $el[0].innerHTML));

            DashTable.getCellById(1, 'ccc')
                .within(() => cy.get('.dash-cell-value')
                    .then($el => cell_1 = $el[0].innerHTML));

            DashTable.getFilterById('ccc').click();
            DOM.focused.type(`gt num(100)`);
            DashTable.getFilterById('ddd').click();
            DOM.focused.type('lt num(20000)');
            DashTable.getFilterById('eee').click();
            DOM.focused.type('is prime');
            DashTable.getFilterById('bbb').click();
            DOM.focused.type(`eq "Wet"`);
            DashTable.getFilterById('ccc').click();

            DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '101'));
            DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '109'));

            cy.get('.clear-filters').click();

            DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_0));
            DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_1));

            DashTable.getFilterById('bbb').within(() => cy.get('input').should('have.value', ''));
            DashTable.getFilterById('ccc').within(() => cy.get('input').should('have.value', ''));
            DashTable.getFilterById('ddd').within(() => cy.get('input').should('have.value', ''));
            DashTable.getFilterById('eee').within(() => cy.get('input').should('have.value', ''));
        });
    });
});