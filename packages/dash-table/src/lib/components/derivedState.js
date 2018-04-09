import * as R from 'ramda';

export function colIsEditable(editable, column) {
    return !(
        !editable ||
        (R.has('editable', column) &&
        !column.editable)
    );
}
