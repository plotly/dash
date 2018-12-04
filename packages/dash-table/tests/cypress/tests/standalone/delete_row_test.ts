import DashTable from 'cypress/DashTable';

import { AppMode } from 'demo/AppMode';

Object.values(AppMode).forEach(mode => {
    describe(`delete, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        it('can delete row', () => {
            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '1'));
            DashTable.getDelete(0).click();
            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '2'));
        });

        it('can delete row when sorted', () => {
            cy.get('tr th.column-0 .sort').last().click({ force: true }).click({ force: true });
            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '4999'));
            DashTable.getDelete(0).click();
            DashTable.getCell(0, 0).within(() => cy.get('.dash-cell-value').should('have.html', '4998'));
        });
    });
});