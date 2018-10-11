import * as R from 'ramda';
import React from 'react';

import Logger from 'core/Logger';

import ColumnFilter from 'dash-table/components/Filter/Column';
import AdvancedFilter from 'dash-table/components/Filter/Advanced';
import { ColumnId, Filtering, FilteringType, IVisibleColumn, VisibleColumns } from 'dash-table/components/Table/props';
import lexer, { ILexerResult, ILexemeResult } from 'core/syntax-tree/lexer';
import { LexemeType } from 'core/syntax-tree/lexicon';
import syntaxer, { ISyntaxerResult, ISyntaxTree } from 'core/syntax-tree/syntaxer';

type SetFilter = (filter: string) => void;

export interface IFilterOptions {
    columns: VisibleColumns;
    fillerColumns: number;
    filtering: Filtering;
    filtering_settings: string;
    filtering_type: FilteringType;
    id: string;
    setFilter: SetFilter;
}

export default class FilterFactory {
    private readonly handlers = new Map();
    private readonly ops = new Map<string, string>();

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => IFilterOptions) {

    }

    private onChange = (columnId: ColumnId, ops: Map<ColumnId, string>, setFilter: SetFilter, ev: any) => {
        Logger.debug('Filter -- onChange', columnId, ev.target.value && ev.target.value.trim());

        const value = ev.target.value.trim();

        if (value && value.length) {
            ops.set(columnId.toString(), value);
        } else {
            ops.delete(columnId.toString());
        }

        setFilter(R.map(
            ([cId, filter]) => `${cId} ${filter}`,
            R.filter(
                ([cId]) => this.isFragmentValid(cId),
                Array.from(ops.entries())
            )
        ).join(' && '));
    }

    private getEventHandler = (fn: Function, columnId: ColumnId, ops: Map<ColumnId, string>, setFilter: SetFilter): any => {
        const fnHandler = (this.handlers.get(fn) || this.handlers.set(fn, new Map()).get(fn));
        const columnIdHandler = (fnHandler.get(columnId) || fnHandler.set(columnId, new Map()).get(columnId));

        return (
            columnIdHandler.get(setFilter) ||
            (columnIdHandler.set(setFilter, fn.bind(this, columnId, ops, setFilter)).get(setFilter))
        );
    }

    private respectsBasicSyntax(lexemes: ILexemeResult[], allowMultiple: boolean = true) {
        const allowedLexemeTypes = [
            LexemeType.BinaryOperator,
            LexemeType.Expression,
            LexemeType.Operand,
            LexemeType.UnaryOperator
        ];

        if (allowMultiple) {
            allowedLexemeTypes.push(LexemeType.And);
        }

        const allAllowed = R.all(
            item => R.contains(item.lexeme.name, allowedLexemeTypes),
            lexemes
        );

        if (!allAllowed) {
            return false;
        }

        const fields = R.map(
            item => item.value,
            R.filter(
                i => i.lexeme.name === LexemeType.Operand,
                lexemes
            )
        );

        const uniqueFields = R.uniq(fields);

        if (fields.length !== uniqueFields.length) {
            return false;
        }

        return true;
    }

    private isBasicFilter(
        lexerResult: ILexerResult,
        syntaxerResult: ISyntaxerResult,
        allowMultiple: boolean = true
    ) {
        return lexerResult.valid &&
            syntaxerResult.valid &&
            this.respectsBasicSyntax(lexerResult.lexemes, allowMultiple);
    }

    private updateOps(query: string) {
        const lexerResult = lexer(query);
        const syntaxerResult = syntaxer(lexerResult);

        if (!this.isBasicFilter(lexerResult, syntaxerResult)) {
            return;
        }

        const { tree } = syntaxerResult;
        const toCheck: (ISyntaxTree | undefined)[] = [tree];

        while (toCheck.length) {
            const item = toCheck.pop();
            if (!item) {
                continue;
            }

            if (item.lexeme.name === LexemeType.UnaryOperator && item.block) {
                this.ops.set(item.block.value, item.value);
            } else if (item.lexeme.name === LexemeType.BinaryOperator && item.left && item.right) {
                this.ops.set(item.left.value, `${item.value} ${item.right.value}`);
            } else {
                toCheck.push(item.left);
                toCheck.push(item.block);
                toCheck.push(item.right);
            }
        }
    }

    private isFragmentValidOrNull(columnId: ColumnId) {
        const op = this.ops.get(columnId.toString());

        return !op || !op.trim().length || this.isFragmentValid(columnId);
    }

    private isFragmentValid(columnId: ColumnId) {
        const op = this.ops.get(columnId.toString());

        const lexerResult = lexer(`${columnId} ${op}`);
        const syntaxerResult = syntaxer(lexerResult);

        return syntaxerResult.valid && this.isBasicFilter(lexerResult, syntaxerResult, false);
    }

    public createFilters() {
        const {
            columns,
            fillerColumns,
            filtering,
            filtering_settings,
            filtering_type,
            setFilter
        } = this.props;

        if (!filtering) {
            return [];
        }

        this.updateOps(filtering_settings);

        const offsetCells = R.range(0, fillerColumns).map(i => (<th key={`offset-${i}`} />));

        const filterCells = filtering_type === FilteringType.Basic ?
            R.addIndex<IVisibleColumn, JSX.Element>(R.map)((column, index) => {
                return (<ColumnFilter
                    key={`column-${index}`}
                    classes={`dash-filter column-${index}`}
                    columnId={column.id}
                    isValid={this.isFragmentValidOrNull(column.id)}
                    property={column.id}
                    setFilter={this.getEventHandler(this.onChange, column.id, this.ops, setFilter)}
                    value={this.ops.get(column.id.toString())}
                />);
            }, columns) :
            [(<AdvancedFilter
                key={`column-${0}`}
                classes={[]}
                colSpan={columns.length}
                value=''
                setFilter={() => undefined}
            />)];

        return [R.concat(offsetCells, filterCells)];
    }
}