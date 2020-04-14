import DOM from './DOM';

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

    public focusedType(text: string, options?: Partial<Cypress.TypeOptions>) {
        return DOM.focused.type(text, options);
    }

    public clickCell(row: number, column: number, editable: State = State.Ready) {
        return this.getCell(row, column, editable).click();
    }

    public clickCellById(row: number, column: string, editable: State = State.Ready) {
        return this.getCellById(row, column, editable).click();
    }

    public clickFilterInput(column: number, editable: State = State.Ready) {
        return this.getFilterInput(column, editable).click();
    }

    public clickFilterInputById(column: string, editable: State = State.Ready) {
        return this.getFilterInputById(column, editable).click();
    }

    public getCell(row: number, column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td.column-${column}:not(.phantom-cell)`).eq(row);
    }

    public getCellById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td[data-dash-column="${column}"]:not(.phantom-cell)`).eq(row);
    }

    public getFilterInput(column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-filter.column-${column}:not(.phantom-cell) input`);
    }

    public getFilterInputById(column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-filter[data-dash-column="${column}"]:not(.phantom-cell) input`);
    }

    public getFilter(column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-filter.column-${column}:not(.phantom-cell)`);
    }

    public getFilterById(column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-filter[data-dash-column="${column}"]:not(.phantom-cell)`);
    }

    public getHeader(row: number, column: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header.column-${column}:not(.phantom-cell)`).eq(row);
    }

    public getHeaderById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"]:not(.phantom-cell)`).eq(row);
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
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"]:not(.phantom-cell) .column-header--clear`).eq(row).click();
    }

    public deleteColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"]:not(.phantom-cell) .column-header--delete`).eq(row).click();
    }

    public hideColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"]:not(.phantom-cell) .column-header--hide`).eq(row).click();
    }

    public getSelectColumnById(row: number, column: string, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr th.dash-header[data-dash-column="${column}"]:not(.phantom-cell) .column-header--select input`).eq(row);
    }

    public selectColumnById(row: number, column: string) {
        return this.getSelectColumnById(row, column).click();
    }

    public getDelete(row: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td.dash-delete-cell:not(.phantom-cell)`).eq(row);
    }

    public getSelect(row: number, editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody tr td.dash-select-cell:not(.phantom-cell)`).eq(row);
    }

    public getActiveCell(editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody td.focused:not(.phantom-cell)`);
    }

    public getSelectedCells(editable: State = State.Ready) {
        return cy.get(`#${this.id} ${getSelector(editable)} tbody td.cell--selected:not(.phantom-cell)`);
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
        const cellInLastRow = cy.get(`td.dash-cell.column-${column}:not(.phantom-cell)`).last().then(elem => {
            const lastRow = elem ? elem.attr(`data-dash-row`) : undefined;
            return lastRow ? cy.get(`td.dash-cell.column-${column}[data-dash-row="${lastRow}"]:not(.phantom-cell)`) : undefined;
        });
        return cellInLastRow;
    }

    public getCellFromDataDash(row: number, column: number) {
        return cy.get(`td.column-${column}[data-dash-row="${row}"]:not(.phantom-cell)`);
    }

    public toggleScroll(toggled: boolean) {
        cy.get('.row-1').then($el => {
            $el[0].style.overflow = toggled ? '' : 'unset';
        });
    }
}

export default new DashTableHelper('table');