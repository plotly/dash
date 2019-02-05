import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

describe(`filter`, () => {
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