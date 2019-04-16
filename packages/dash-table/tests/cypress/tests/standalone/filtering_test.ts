import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

describe(`filter special characters`, () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.ColumnsInSpace}`);
        DashTable.toggleScroll(false);
    });

    it('can filter on special column id', () => {
        DashTable.getFilterById('b+bb').click();
        DOM.focused.type(`Wet${Key.Enter}`);

        DashTable.getFilterById('c cc').click();
        DOM.focused.type(`gt 90${Key.Enter}`);

        DashTable.getFilterById('d:dd').click();
        DOM.focused.type(`lt 12500${Key.Enter}`);

        DashTable.getFilterById('e-ee').click();
        DOM.focused.type(`is prime${Key.Enter}`);

        DashTable.getFilterById('f_ff').click();
        DOM.focused.type(`le 106${Key.Enter}`);

        DashTable.getFilterById('g.gg').click();
        DOM.focused.type(`gt 1000${Key.Enter}`);
        DashTable.getFilterById('b+bb').click();

        DashTable.getCellById(0, 'rows').within(() => cy.get('.dash-cell-value').should('have.html', '101'));
        DashTable.getCellById(1, 'rows').should('not.exist');
        DashTable.getFilterById('b+bb').within(() => cy.get('input').should('have.value', 'Wet'));
        DashTable.getFilterById('c cc').within(() => cy.get('input').should('have.value', 'gt 90'));
        DashTable.getFilterById('d:dd').within(() => cy.get('input').should('have.value', 'lt 12500'));
        DashTable.getFilterById('e-ee').within(() => cy.get('input').should('have.value', 'is prime'));
        DashTable.getFilterById('f_ff').within(() => cy.get('input').should('have.value', 'le 106'));
        DashTable.getFilterById('g.gg').within(() => cy.get('input').should('have.value', 'gt 1000'));
    });
});

describe('filter', () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Filtering}`);
        DashTable.toggleScroll(false);
    });

    it('handles hovering onto other filtering cells', () => {
        DashTable.getFilterById('ccc').click();
        DOM.focused.type(`gt 100`);
        DashTable.getFilterById('ddd').click();
        DOM.focused.type('lt 20000');

        DashTable.getCellById(0, 'eee').trigger('mouseover');

        DashTable.getFilterById('ccc').within(() => cy.get('input').should('have.value', 'gt 100'));
        DashTable.getFilterById('ddd').within(() => cy.get('input').should('have.value', 'lt 20000'));
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

        DashTable.getFilterById('ccc').click();
        DOM.focused.type(`gt`);
        DashTable.getFilterById('ddd').click();
        DOM.focused.type('20 a000');
        DashTable.getFilterById('eee').click();
        DOM.focused.type('is prime2');
        DashTable.getFilterById('bbb').click();
        DOM.focused.type('! !');
        DashTable.getFilterById('ccc').click();

        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_0));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_1));

        DashTable.getFilterById('bbb').within(() => cy.get('input').should('have.value', '! !'));
        DashTable.getFilterById('ccc').within(() => cy.get('input').should('have.value', 'gt'));
        DashTable.getFilterById('ddd').within(() => cy.get('input').should('have.value', '20 a000'));
        DashTable.getFilterById('eee').within(() => cy.get('input').should('have.value', 'is prime2'));

        DashTable.getFilterById('bbb').should('have.class', 'invalid');
        DashTable.getFilterById('ccc').should('have.class', 'invalid');
        DashTable.getFilterById('ddd').should('have.class', 'invalid');
        DashTable.getFilterById('eee').should('have.class', 'invalid');
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

        DashTable.getFilterById('ccc').click();
        DOM.focused.type(`gt 100`);
        DashTable.getFilterById('ddd').click();
        DOM.focused.type('lt 20000');
        DashTable.getFilterById('eee').click();
        DOM.focused.type('is prime');
        DashTable.getFilterById('bbb').click();
        DOM.focused.type(`Wet`);
        DashTable.getFilterById('ccc').click();

        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '101'));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', '109'));

        DashTable.getFilterById('bbb').within(() => cy.get('input').should('have.value', 'Wet'));
        DashTable.getFilterById('ccc').within(() => cy.get('input').should('have.value', 'gt 100'));
        DashTable.getFilterById('ddd').within(() => cy.get('input').should('have.value', 'lt 20000'));
        DashTable.getFilterById('eee').within(() => cy.get('input').should('have.value', 'is prime'));

        cy.get('.clear-filters').click();

        DashTable.getCellById(0, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_0));
        DashTable.getCellById(1, 'ccc').within(() => cy.get('.dash-cell-value').should('have.html', cell_1));

        DashTable.getFilterById('bbb').within(() => cy.get('input').should('have.value', ''));
        DashTable.getFilterById('ccc').within(() => cy.get('input').should('have.value', ''));
        DashTable.getFilterById('ddd').within(() => cy.get('input').should('have.value', ''));
        DashTable.getFilterById('eee').within(() => cy.get('input').should('have.value', ''));
    });
});