import { StyleProperty } from './py2jsCssProperties';
import { ColumnId } from 'dash-table/components/Table/props';

export interface IConditionalElement {
    filter?: string;
}

export interface IIndexedHeaderElement {
    header_index?: number | 'odd' | 'even';
}

export interface IIndexedRowElement {
    row_index?: number | 'odd' | 'even';
}

export interface INamedElement {
    column_id?: ColumnId;
}

type ConditionalCell = IConditionalElement & IIndexedRowElement & INamedElement;
type ConditionalCellAndHeader = INamedElement;
type ConditionalHeader = IIndexedHeaderElement & INamedElement;

interface IStyle {
    background: StyleProperty;
    background_attachment: StyleProperty;
    background_color: StyleProperty;
    background_image: StyleProperty;
    background_position: StyleProperty;
    background_repeat: StyleProperty;
    border: StyleProperty;
    border_bottom: StyleProperty;
    border_bottom_color: StyleProperty;
    border_bottom_style: StyleProperty;
    border_bottom_width: StyleProperty;
    border_color: StyleProperty;
    border_left: StyleProperty;
    border_left_color: StyleProperty;
    border_left_style: StyleProperty;
    border_left_width: StyleProperty;
    border_right: StyleProperty;
    border_right_color: StyleProperty;
    border_right_style: StyleProperty;
    border_right_width: StyleProperty;
    border_style: StyleProperty;
    border_top: StyleProperty;
    border_top_color: StyleProperty;
    border_top_style: StyleProperty;
    border_top_width: StyleProperty;
    border_width: StyleProperty;
    clear: StyleProperty;
    clip: StyleProperty;
    color: StyleProperty;
    cursor: StyleProperty;
    display: StyleProperty;
    filter: StyleProperty;
    float: StyleProperty;
    font: StyleProperty;
    font_family: StyleProperty;
    font_size: StyleProperty;
    font_variant: StyleProperty;
    font_weight: StyleProperty;
    height: StyleProperty;
    left: StyleProperty;
    letter_spacing: StyleProperty;
    line_height: StyleProperty;
    list_style: StyleProperty;
    list_style_image: StyleProperty;
    list_style_position: StyleProperty;
    list_style_type: StyleProperty;
    margin: StyleProperty;
    margin_bottom: StyleProperty;
    margin_left: StyleProperty;
    margin_right: StyleProperty;
    margin_top: StyleProperty;
    max_width: StyleProperty;
    min_width: StyleProperty;
    overflow: StyleProperty;
    padding: StyleProperty;
    padding_bottom: StyleProperty;
    padding_left: StyleProperty;
    padding_right: StyleProperty;
    padding_top: StyleProperty;
    page_break_after: StyleProperty;
    page_break_before: StyleProperty;
    position: StyleProperty;
    stroke_dasharray: StyleProperty;
    stroke_dashoffset: StyleProperty;
    stroke_width: StyleProperty;
    text_align: StyleProperty;
    text_decoration: StyleProperty;
    text_indent: StyleProperty;
    text_transform: StyleProperty;
    top: StyleProperty;
    vertical_align: StyleProperty;
    visibility: StyleProperty;
    width: StyleProperty;
    z_index: StyleProperty;

    // CSS props
    'background-attachment': StyleProperty;
    'background-color': StyleProperty;
    'background-image': StyleProperty;
    'background-position': StyleProperty;
    'background-repeat': StyleProperty;
    'border-bottom': StyleProperty;
    'border-bottom-color': StyleProperty;
    'border-bottom-style': StyleProperty;
    'border-bottom-width': StyleProperty;
    'border-color': StyleProperty;
    'border-left': StyleProperty;
    'border-left-color': StyleProperty;
    'border-left-style': StyleProperty;
    'border-left-width': StyleProperty;
    'border-right': StyleProperty;
    'border-right-color': StyleProperty;
    'border-right-style': StyleProperty;
    'border-right-width': StyleProperty;
    'border-style': StyleProperty;
    'border-top': StyleProperty;
    'border-top-color': StyleProperty;
    'border-top-style': StyleProperty;
    'border-top-width': StyleProperty;
    'border-width': StyleProperty;
    'font-family': StyleProperty;
    'font-size': StyleProperty;
    'font-variant': StyleProperty;
    'font-weight': StyleProperty;
    'letter-spacing': StyleProperty;
    'line-height': StyleProperty;
    'list-style': StyleProperty;
    'list-style-image': StyleProperty;
    'list-style-position': StyleProperty;
    'list-style-type': StyleProperty;
    'margin-bottom': StyleProperty;
    'margin-left': StyleProperty;
    'margin-right': StyleProperty;
    'margin-top': StyleProperty;
    'max-width': StyleProperty;
    'min-width': StyleProperty;
    'padding-bottom': StyleProperty;
    'padding-left': StyleProperty;
    'padding-right': StyleProperty;
    'padding-top': StyleProperty;
    'page-break-after': StyleProperty;
    'page-break-before': StyleProperty;
    'stroke-dasharray': StyleProperty;
    'stroke-dashoffset': StyleProperty;
    'stroke-width': StyleProperty;
    'text-align': StyleProperty;
    'text-decoration': StyleProperty;
    'text-indent': StyleProperty;
    'text-transform': StyleProperty;
    'vertical-align': StyleProperty;
    'z-index': StyleProperty;

    // JS props
    backgroundAttachment: StyleProperty;
    backgroundColor: StyleProperty;
    backgroundImage: StyleProperty;
    backgroundPosition: StyleProperty;
    backgroundRepeat: StyleProperty;
    borderBottom: StyleProperty;
    borderBottomColor: StyleProperty;
    borderBottomStyle: StyleProperty;
    borderBottomWidth: StyleProperty;
    borderColor: StyleProperty;
    borderLeft: StyleProperty;
    borderLeftColor: StyleProperty;
    borderLeftStyle: StyleProperty;
    borderLeftWidth: StyleProperty;
    borderRight: StyleProperty;
    borderRightColor: StyleProperty;
    borderRightStyle: StyleProperty;
    borderRightWidth: StyleProperty;
    borderStyle: StyleProperty;
    borderTop: StyleProperty;
    borderTopColor: StyleProperty;
    borderTopStyle: StyleProperty;
    borderTopWidth: StyleProperty;
    borderWidth: StyleProperty;
    cssFloat: StyleProperty;
    fontFamily: StyleProperty;
    fontSize: StyleProperty;
    fontVariant: StyleProperty;
    fontWeight: StyleProperty;
    letterSpacing: StyleProperty;
    lineHeight: StyleProperty;
    listStyle: StyleProperty;
    listStyleImage: StyleProperty;
    listStylePosition: StyleProperty;
    listStyleType: StyleProperty;
    marginBottom: StyleProperty;
    marginLeft: StyleProperty;
    marginRight: StyleProperty;
    marginTop: StyleProperty;
    maxWidth: StyleProperty;
    minWidth: StyleProperty;
    paddingBottom: StyleProperty;
    paddingLeft: StyleProperty;
    paddingRight: StyleProperty;
    paddingTop: StyleProperty;
    pageBreakAfter: StyleProperty;
    pageBreakBefore: StyleProperty;
    strokeDasharray: StyleProperty;
    strokeDashoffset: StyleProperty;
    strokeWidth: StyleProperty;
    textAlign: StyleProperty;
    textDecoration: StyleProperty;
    textIndent: StyleProperty;
    textTransform: StyleProperty;
    verticalAlign: StyleProperty;
    zIndex: StyleProperty;
}

export type Style = Partial<IStyle>;

export type Cell = Style & { if: ConditionalCell };
export type CellAndHeader = Style & { if: ConditionalCellAndHeader };
export type Header = Style & { if: ConditionalHeader };

export type Cells = Cell[];
export type CellsAndHeaders = CellAndHeader[];
export type Headers = Header[];
export type Table = Style;