export const Type = 'pandas.DataFrame';

// https://github.com/ironSource/parquetjs
const fromParquet = async (_parquetFile, _engine) => {
    // TODO: do some reading stuff
    /*
    let reader = await parquet.ParquetReader.openFile('fruits.parquet');
    // create a new cursor
    let cursor = reader.getCursor();

    // read all records from the file and print them
    let record = null;
    while (record = await cursor.next()) {
    console.log(record);
    }
    */

    return new Promise((resolve, _reject) => {
        setTimeout(() => {
            resolve();
        }, 50);
    });
};


export const toParquet = async (_value, _engine) => {
    // TODO: do some writing stuff
    /*
    // create new ParquetWriter that writes to 'fruits.parquet`
    var writer = await parquet.ParquetWriter.openFile(schema, 'fruits.parquet');

    // append a few rows to the file
    await writer.appendRow({name: 'apples', quantity: 10, price: 2.5, date: new Date(), in_stock: true});
    await writer.appendRow({name: 'oranges', quantity: 10, price: 2.5, date: new Date(), in_stock: true});
    Once we are finished adding rows to the file, we have to tell the writer object to flush the metadata to disk and close the file by calling the close() method:
    await writer.close();
    */

    return new Promise((resolve, _reject) => {
        setTimeout(() => {
            resolve();
        }, 50);
    });
};

// TODO: Implement `toParquet` and `fromeParquet`
export const serialize = toParquet;
export const deserialize = fromParquet;
