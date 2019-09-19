const READY = `.dash-spreadsheet:not(.dash-loading)`;
const LOADING = `.dash-spreadsheet.dash-loading`;
const ANY = `.dash-spreadsheet`;

export enum State {
    Any,
    Loading,
    Ready
}

const getSelector = (state: State) => {
    switch (state) {
        case State.Ready:
            return READY;
        case State.Loading:
            return LOADING;
        default:
            return ANY;
    }
};

export class DashTableHelper {
    constructor(private readonly id) {

    }

    public getCell(row: number, column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td.column-${column}`).eq(row);
    }

    public getCellById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td[data-dash-column="${column}"]`).eq(row);
    }

    public getFilter(column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-filter.column-${column}`);
    }

    public getFilterById(column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-filter[data-dash-column="${column}"]`);
    }

    public getHeader(row: number, column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header.column-${column}`).eq(row);
    }

    public getHeaderById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"]`).eq(row);
    }

    public focusCell(row: number, column: number) {
        // somehow we need to scrollIntoView AFTER click, or it doesn't
        // work right. Why?
        return this.getCell(row, column).click().scrollIntoView();
    }

    public focusCellById(row: number, column: string) {
        return this.getCellById(row, column).click().scrollIntoView();
    }

    public clearColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"] .column-header--clear`).eq(row).click();
    }

    public deleteColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"] .column-header--delete`).eq(row).click();
    }

    public hideColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"] .column-header--hide`).eq(row).click();
    }

    public getSelectColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"] .column-header--select input`).eq(row);
    }

    public selectColumnById(row: number, column: string) {
        return this.getSelectColumnById(row, column).click();
    }

    public getDelete(row: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td.dash-delete-cell`).eq(row);
    }

    public getSelect(row: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td.dash-select-cell`).eq(row);
    }

    public getActiveCell(editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody td.focused`);
    }

    public getSelectedCells(editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody td.cell--selected`);
    }

    public scrollToTop() {
        cy.get(`.cell.cell-1-1.dash-fixed-content`).invoke(`outerHeight`).then(height => {
            cy.scrollTo(0, -height);
        });
    }

    public scrollToBottom() {
        cy.get(`.cell.cell-1-1.dash-fixed-content`).invoke(`outerHeight`).then(height => {
            cy.scrollTo(0, height);
        });
    }

    public getCellInLastRowOfColumn(column: number) {
        const cellInLastRow = cy.get(`td.dash-cell.column-${column}`).last().then(elem => {
            const lastRow = elem ? elem.attr(`data-dash-row`) : undefined;
            return lastRow ? cy.get(`td.dash-cell.column-${column}[data-dash-row="${lastRow}"`) : undefined;
        });
        return cellInLastRow;
    }

    public getCellFromDataDash(row: number, column: number) {
        return cy.get(`td.column-${column}[data-dash-row="${row}"]`);
    }

    public toggleScroll(toggled: boolean) {
        cy.get('.row-1').then($el => {
            $el[0].style.overflow = toggled ? '' : 'unset';
        });
    }
}

export default new DashTableHelper('table');