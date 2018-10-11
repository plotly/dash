import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeAll, memoizeOne } from 'core/memoizer';
import { ColumnId, Dataframe, Datum, VisibleColumns } from 'dash-table/components/Table/props';
import SyntaxTree from 'core/syntax-tree';
import memoizerCache from 'core/memoizerCache';

interface IStyle {
    target?: undefined;
    style: CSSProperties;
}

interface IConditionalStyle extends IStyle {
    condition: string;
}

type Style = CSSProperties | undefined;

type Key = [ColumnId, number];
type AstCacheFn = (key: Key, query: string) => SyntaxTree;
type StyleCacheFn = (
    key: Key,
    astCache: AstCacheFn,
    conditionalStyles: IConditionalStyle[],
    datum: Datum,
    property: ColumnId,
    staticStyle: IStyle
) => Style;

const NULL_CONDITIONAL_STYLES: IConditionalStyle[] = [];

function getStyle(
    astCache: AstCacheFn,
    conditionalStyles: IConditionalStyle[],
    datum: Datum,
    property: ColumnId,
    staticStyle: IStyle
) {
    const styles = R.map(
        ([cs]) => cs.style,
        R.filter(
            ([cs, i]) => astCache([property, i], cs.condition).evaluate(datum),
            R.addIndex<IConditionalStyle, [IConditionalStyle, number]>(R.map)(
                (cs, i) => [cs, i],
                conditionalStyles
            )
        )
    );

    if (staticStyle) {
        styles.push(staticStyle.style);
    }

    if (!styles.length) {
        return undefined;
    }

    return R.mergeAll<CSSProperties>(styles);
}

function getter(
    astCache: AstCacheFn,
    styleCache: StyleCacheFn,
    columns: VisibleColumns,
    columnConditionalStyle: any,
    columnStaticStyle: any,
    dataframe: Dataframe
): Style[][] {
    return R.addIndex<any, any>(R.map)(
        (datum, rowIndex) => R.addIndex<any, any>(R.map)(
            (column, columnIndex) => {
                let conditionalStyles = columnConditionalStyle.find((cs: any) => cs.id === column.id);
                let staticStyle = columnStaticStyle.find((ss: any) => ss.id === column.id);

                conditionalStyles = (conditionalStyles && conditionalStyles.styles) || NULL_CONDITIONAL_STYLES;
                staticStyle = staticStyle && staticStyle.style;

                return styleCache(
                    [rowIndex, columnIndex],
                    astCache,
                    conditionalStyles,
                    datum[column.id],
                    column.id,
                    staticStyle
                );
            },
            columns),
        dataframe);
}

function decorator(_id: string): ((
    columns: VisibleColumns,
    columnConditionalStyle: any,
    columnStaticStyle: any,
    dataframe: Dataframe
) => Style[][]) {
    const astCache = memoizerCache<Key, [string], SyntaxTree>(
        (query: string) => new SyntaxTree(query)
    );

    const styleCache = memoizerCache<
        Key,
        [
            (key: Key, query: string) => SyntaxTree,
            IConditionalStyle[],
            Datum,
            ColumnId,
            IStyle
        ],
        Style
        >(getStyle);

    return memoizeOne(getter).bind(undefined, astCache, styleCache);
}

export default memoizeAll(decorator);
