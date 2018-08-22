export default class DashTable {
    static getCell(row: number, column: number) {
        return cy.get(`#table tbody tr td.column-${column}`).eq(row);
    }

    static getSelectedCells() {
        return cy.get(`#table tbody td.cell--selected`);
    }
}