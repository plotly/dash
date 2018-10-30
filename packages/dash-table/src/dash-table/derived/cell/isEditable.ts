export default (
    isEditableTable: boolean,
    isEditableColumn: boolean | undefined
): boolean => isEditableColumn === undefined ?
        isEditableTable :
        isEditableColumn;