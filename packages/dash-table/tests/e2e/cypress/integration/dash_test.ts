import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';
import Resolve from 'cypress/Resolve';

describe('dash basic', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8081');
    });

    it('can get cell', () => {
        DashTable.getCell(0, 0).click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '0'));

        cy.get('button.next-page').click();
        DashTable.getCell(0, 0).within(() => cy.get('input').should('have.value', '250'));
    });

    // https://github.com/plotly/dash-table/issues/50
    it('can edit last and update dataframe on "enter"', async () => {
        DashTable.getCell(249, 0).click();

        const initialValue = await Resolve(DOM.focused.then($input => {
            return $input.val();
        }));

        DOM.focused.type(`abc${Key.Enter}`);

        cy.get('#container').should('have.value', `[249][0] = ${initialValue} -> abc${initialValue}`);
    });
});