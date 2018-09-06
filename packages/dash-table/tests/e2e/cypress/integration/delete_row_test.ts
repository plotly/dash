import DashTable from 'cypress/DashTable';

describe('delete', () => {
    describe('be', () => {
        beforeEach(() => cy.visit('http://localhost:8081'));

        it('can delete row', () => {
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '0'));
            DashTable.getDelete(0).click();
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '1'));
        });

        it('can delete row when sorted', () => {
            cy.get('tr th.column-2 .filter').click();
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '249'));
            DashTable.getDelete(0).click();
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '248'));
        });
    });

    describe('fe', () => {
        beforeEach(() => cy.visit('http://localhost:8080'));

        it('can delete row', () => {
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '1'));
            DashTable.getDelete(0).click();
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '2'));
        });

        it('can delete row when sorted', () => {
            cy.get('tr th.column-2 .filter').click();
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '4999'));
            DashTable.getDelete(0).click();
            DashTable.getCell(0, 2).within(() => cy.get('.cell-value').should('have.html', '4998'));
        });
    });
});