export default class DictDataFrameSerializer {
    static deserialize = value => {
      const {columns, records} = value;
      const columnOrders = (records || []).length < 0 ? [] : Object.keys(records[0]);
      console.log('columns = ', columns);
      console.log('columnOrders = ', columnOrders);
      return records;
    };

    static serialize = _value => {
      return _value;
    };
}
