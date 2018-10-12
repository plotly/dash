export default class DashTable {
    static getCell(row: number, column: number) {
        return cy.get(`#table tbody tr td.column-${column}`).eq(row);
    }

    static getCellById(row: number, column: number | string) {
        return cy.get(`#table tbody tr td[data-dash-column="${column}"]`).eq(row);
    }

    static getDelete(row: number) {
        return cy.get(`#table tbody tr td.dash-delete-cell`).eq(row);
    }

    static getSelect(row: number) {
        return cy.get(`#table tbody tr td.dash-select-cell`).eq(row);
    }

    static getSelectedCells() {
        return cy.get(`#table tbody td.cell--selected`);
    }
}