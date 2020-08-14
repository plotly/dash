export default (tableFlag: boolean, columnFlag: boolean | undefined): boolean =>
    columnFlag === undefined ? tableFlag : columnFlag;
