import React, {Component} from 'react';
import {IPageNavigationProps} from 'dash-table/components/PageNavigation/props';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {KEY_CODES} from 'dash-table/utils/unicode';

export default class PageNavigation extends Component<IPageNavigationProps> {
    constructor(props: IPageNavigationProps) {
        super(props);
    }

    goToPage = (page_number: string) => {
        const {paginator} = this.props;

        const page = parseInt(page_number, 10);

        if (isNaN(page)) {
            return;
        }

        paginator.loadPage(page - 1);
    };

    render() {
        const {paginator, page_current} = this.props;

        if (paginator.lastPage !== undefined && paginator.lastPage <= 0) {
            return null;
        }

        const pageChars = Math.max(
            3,
            ((paginator.lastPage ?? 0) + 1).toString().length
        );
        const minWidth = `${pageChars + 1}ch`;

        return (
            <div className='previous-next-container'>
                <button
                    className='first-page'
                    onClick={paginator.loadFirst}
                    disabled={!paginator.hasPrevious()}
                >
                    <FontAwesomeIcon icon='angle-double-left' />
                </button>

                <button
                    className='previous-page'
                    onClick={paginator.loadPrevious}
                    disabled={!paginator.hasPrevious()}
                >
                    <FontAwesomeIcon icon='angle-left' />
                </button>

                <div className='page-number'>
                    <div className='current-page-container'>
                        <div className='current-page-shadow' style={{minWidth}}>
                            {(page_current + 1).toString()}
                        </div>
                        <input
                            type='text'
                            className='current-page'
                            style={{minWidth}}
                            onBlur={event => {
                                this.goToPage(event.target.value);
                                event.target.value = '';
                            }}
                            onKeyDown={event => {
                                if (event.keyCode === KEY_CODES.ENTER) {
                                    event.currentTarget.blur();
                                }
                            }}
                            placeholder={(page_current + 1).toString()}
                            defaultValue=''
                        ></input>
                    </div>

                    {paginator.lastPage !== undefined ? ' / ' : ''}

                    {paginator.lastPage !== undefined ? (
                        <div className='last-page' style={{minWidth}}>
                            {paginator.lastPage + 1}
                        </div>
                    ) : (
                        ''
                    )}
                </div>

                <button
                    className='next-page'
                    onClick={paginator.loadNext}
                    disabled={!paginator.hasNext()}
                >
                    <FontAwesomeIcon icon='angle-right' />
                </button>

                <button
                    className='last-page'
                    onClick={paginator.loadLast}
                    disabled={
                        paginator.lastPage === undefined || paginator.isLast()
                    }
                >
                    <FontAwesomeIcon icon='angle-double-right' />
                </button>
            </div>
        );
    }
}
