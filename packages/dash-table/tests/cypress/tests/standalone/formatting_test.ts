import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';
import { AppMode } from 'demo/AppMode';

describe('formatting', () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Formatting}`);
        DashTable.toggleScroll(false);
    });

    it('can edit formatted cell', () => {
        DashTable.getCellById(1, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', 'N/A')
        );
        DashTable.getCellById(1, 'eee').click();
        DOM.focused.type(`1${Key.Enter}`);
        DashTable.getCellById(1, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', '1')
        );
        DashTable.getCellById(1, 'eee').click();
        DOM.focused.type(`abc${Key.Enter}`);
        DashTable.getCellById(1, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', 'N/A')
        );
    });

    it('can copy formatted cell and reformat based on destination cell rules', () => {
        DashTable.getCellById(2, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', '3')
        );
        DashTable.getCellById(2, 'eee').click();
        DOM.focused.type(`${Key.Shift}${Key.ArrowDown}${Key.ArrowDown}`);
        DOM.focused.type(`${Key.Meta}c`);

        DashTable.getCellById(2, 'ddd').click();
        DOM.focused.type(`${Key.Meta}v`);

        DashTable.getCellById(2, 'eee').click();

        DashTable.getCellById(2, 'ddd').within(
            () => cy.get('.dash-cell-value').should('have.html', 'eq. $ 3.00')
        );
        DashTable.getCellById(3, 'ddd').within(
            () => cy.get('.dash-cell-value').should('have.html', 'eq. $ 0.00')
        );
        DashTable.getCellById(4, 'ddd').within(
            () => cy.get('.dash-cell-value').should('have.html', 'eq. $ 0.00')
        );
    });
});