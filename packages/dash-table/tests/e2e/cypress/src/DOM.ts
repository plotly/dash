export default class DOM {
    static get focused() {
        return cy.focused().first();
    }
}
