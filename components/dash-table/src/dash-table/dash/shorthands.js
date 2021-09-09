const generateRecord = (columns, dataRow) => {
    const record = {}
    for (const [i, v] of dataRow.entries()) {
        Object.assign(record, {[columns[i]]:v})
    }

    return record
}

export default props => {
    const {data = [], columns = []} = props
    let resolvedColumns = columns
    let resolvedData = data

    if (data.columns) {
        resolvedData = data.data.map(dataRow => generateRecord(data.columns, dataRow))
        resolvedColumns = data.columns.map(name => ({id: name, name}))
    }

    return {
        ...props,
        data: resolvedData,
        columns: resolvedColumns
    }
}
