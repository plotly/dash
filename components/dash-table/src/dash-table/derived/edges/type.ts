import * as R from 'ramda';
import {CSSProperties} from 'react';

import {OptionalMap, OptionalProp, PropOf} from 'core/type';
import {KnownCssProperties} from '../style/py2jsCssProperties';
import {shallowClone} from 'core/math/matrixZipMap';

export type Edge = any;

export type BorderProp =
    | PropOf<CSSProperties, 'borderBottom'>
    | PropOf<CSSProperties, 'borderLeft'>
    | PropOf<CSSProperties, 'borderRight'>
    | PropOf<CSSProperties, 'borderTop'>;

export type BorderStyle = OptionalMap<
    CSSProperties,
    'borderBottom',
    [OptionalProp<CSSProperties, 'borderBottom'>, number]
> &
    OptionalMap<
        CSSProperties,
        'borderLeft',
        [OptionalProp<CSSProperties, 'borderLeft'>, number]
    > &
    OptionalMap<
        CSSProperties,
        'borderRight',
        [OptionalProp<CSSProperties, 'borderRight'>, number]
    > &
    OptionalMap<
        CSSProperties,
        'borderTop',
        [OptionalProp<CSSProperties, 'borderTop'>, number]
    >;

export const BORDER_PROPERTIES: BorderProp[] = [
    'borderBottom',
    'borderLeft',
    'borderRight',
    'borderTop'
];

export const BORDER_PROPERTIES_AND_FRAGMENTS: string[] = R.filter(
    p => p.indexOf('border') === 0,
    KnownCssProperties
);

export interface IEdgesMatrix {
    getEdge(i: number, j: number): Edge;
    getEdges(): Edge[][];
    getWeight(i: number, j: number): number;
    isDefault(i: number, j: number): boolean;
}

export interface IEdgesMatrices {
    getEdges(): {
        horizontal: Edge[][];
        vertical: Edge[][];
    };
    getMatrices(): {
        horizontal: EdgesMatrix;
        vertical: EdgesMatrix;
    };
    getStyle(i: number, j: number): CSSProperties;
}

export class EdgesMatrix implements IEdgesMatrix {
    private weights: number[][];
    private edges: Edge[][];

    public readonly rows: number;
    public readonly columns: number;
    public readonly defaultEdge: Edge | undefined;

    constructor(m: EdgesMatrix);
    constructor(rows: number, columns: number, defaultEdge?: Edge);
    constructor(
        rowsOrMatrix: number | EdgesMatrix,
        columns?: number,
        defaultEdge?: Edge
    ) {
        if (
            typeof rowsOrMatrix === 'number' &&
            typeof columns !== 'undefined'
        ) {
            const rows = rowsOrMatrix;

            this.rows = rows;
            this.columns = columns;
            this.defaultEdge = defaultEdge;

            this.weights = R.map(
                () => new Array(columns).fill(-Infinity),
                R.range(0, rows)
            );

            this.edges = R.map(
                () => new Array(columns).fill(defaultEdge),
                R.range(0, rows)
            );
        } else {
            const source = rowsOrMatrix as EdgesMatrix;

            this.rows = source.rows;
            this.columns = source.columns;
            this.defaultEdge = source.defaultEdge;

            this.weights = shallowClone(source.weights);
            this.edges = shallowClone(source.edges);
        }
    }

    setEdge(i: number, j: number, edge: Edge, weight: number, force = false) {
        if (i < 0 || j < 0 || i >= this.rows || j >= this.columns) {
            return;
        }

        if (!force && (R.isNil(edge) || weight <= this.weights[i][j])) {
            return;
        }

        this.weights[i][j] = weight;
        this.edges[i][j] = edge;
    }

    getEdge = (i: number, j: number) => this.edges[i][j];

    getEdges = () => this.edges;

    getWeight = (i: number, j: number) => this.weights[i][j];

    isDefault = (i: number, j: number) => this.weights[i][j] === -Infinity;

    clone = () => new EdgesMatrix(this);
}

export class EdgesMatrices implements IEdgesMatrices {
    private readonly horizontal: EdgesMatrix;
    private readonly vertical: EdgesMatrix;

    private readonly horizontalEdges: boolean;
    private readonly verticalEdges: boolean;

    private readonly rows: number;
    private readonly columns: number;
    private readonly defaultEdge: Edge | undefined;

    constructor(m: EdgesMatrices);
    constructor(
        rows: number,
        columns: number,
        defaultEdge: Edge | undefined,
        horizontalEdges?: boolean,
        verticalEdges?: boolean
    );
    constructor(
        rowsOrMatrix: number | EdgesMatrices,
        columns?: number,
        defaultEdge?: Edge,
        horizontalEdges?: boolean,
        verticalEdges?: boolean
    ) {
        if (
            typeof rowsOrMatrix === 'number' &&
            typeof columns !== 'undefined'
        ) {
            const rows = rowsOrMatrix;

            this.rows = rows;
            this.columns = columns;
            this.defaultEdge = defaultEdge;

            this.horizontalEdges = R.isNil(horizontalEdges) || horizontalEdges;
            this.verticalEdges = R.isNil(verticalEdges) || verticalEdges;

            this.horizontal = new EdgesMatrix(
                rows + 1,
                columns,
                this.horizontalEdges ? defaultEdge : undefined
            );
            this.vertical = new EdgesMatrix(
                rows,
                columns + 1,
                this.verticalEdges ? defaultEdge : undefined
            );
        } else {
            const source = rowsOrMatrix as EdgesMatrices;

            this.rows = source.rows;
            this.columns = source.columns;
            this.defaultEdge = source.defaultEdge;

            this.horizontal = source.horizontal.clone();
            this.vertical = source.vertical.clone();

            this.horizontalEdges = source.horizontalEdges;
            this.verticalEdges = source.verticalEdges;
        }
    }

    setEdges(i: number, j: number, style: BorderStyle) {
        if (this.horizontalEdges) {
            if (style.borderTop) {
                this.horizontal.setEdge(
                    i,
                    j,
                    style.borderTop[0],
                    style.borderTop[1]
                );
            }

            if (style.borderBottom) {
                this.horizontal.setEdge(
                    i + 1,
                    j,
                    style.borderBottom[0],
                    style.borderBottom[1]
                );
            }
        }

        if (this.verticalEdges) {
            if (style.borderLeft) {
                this.vertical.setEdge(
                    i,
                    j,
                    style.borderLeft[0],
                    style.borderLeft[1]
                );
            }

            if (style.borderRight) {
                this.vertical.setEdge(
                    i,
                    j + 1,
                    style.borderRight[0],
                    style.borderRight[1]
                );
            }
        }
    }

    getEdges = () => ({
        horizontal: this.horizontal.getEdges(),
        vertical: this.vertical.getEdges()
    });

    getMatrices = () => ({
        horizontal: this.horizontal,
        vertical: this.vertical
    });

    getStyle = (i: number, j: number): CSSProperties => ({
        borderBottom: this.horizontal.getEdge(i + 1, j) || null,
        borderTop: this.horizontal.getEdge(i, j) || null,
        borderLeft: this.vertical.getEdge(i, j) || null,
        borderRight: this.vertical.getEdge(i, j + 1) || null
    });

    clone = () => new EdgesMatrices(this);
}
