import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('edit cell', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8080');
    });

    // https://github.com/plotly/dash-table/issues/50
    it('can edit on "enter"', () => {
        DashTable.getCell(0, 3).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

            DOM.focused.type(`abc${Key.Enter}`);
            DashTable.getCell(0, 3).within(() => cy.get('.cell-value').should('have.html', `abc${initialValue}`));
        });
    });

    it('can edit when clicking outside of cell', () => {
        DashTable.getCell(0, 3).click();
        DOM.focused.then($input => {
            const initialValue = $input.val();

            DOM.focused.type(`abc`);
            DashTable.getCell(0, 2).click();
            DashTable.getCell(0, 3).within(() => cy.get('.cell-value').should('have.html', `abc${initialValue}`));
        });
    });
});