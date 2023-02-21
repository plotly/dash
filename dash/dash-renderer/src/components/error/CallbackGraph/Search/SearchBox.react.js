import {useEffect, useRef, useState} from 'react';
import {SearchBoxItem} from './SearchBoxItem.react';

import './SearchBox.css';

export function SearchBox(props) {
    const [searchTerm, setSearchTerm] = useState('');

    const searchBoxRef = useRef(null);
    const optionsContainer = useRef(null);

    const onItemClickHandler = event => {
        searchBoxRef.current.blur();
        searchBoxRef.current.value = '';
        setSearchTerm('');

        optionsContainer.current.classList.toggle('active');

        props.onSelectionChanged(event);
    };

    useEffect(() => {
        const arr = Array.from(optionsContainer.current.children);
        const total = arr.reduce((subtotal, child) => {
            if (!child.classList.contains('hidden')) {
                subtotal += 1;
            }
            return subtotal;
        }, 0);

        if (total === 0) {
            // no items found action
        }
    });

    const searchBoxExit = () => {
        optionsContainer.current.classList.toggle('active');

        searchBoxRef.current.blur();
        searchBoxRef.current.value = '';
        setSearchTerm('');
    };

    const searchBoxClicked = () => {
        optionsContainer.current.classList.toggle('active');

        if (optionsContainer.current.classList.contains('active')) {
            searchBoxRef.current.focus();
        } else {
            searchBoxRef.current.blur();
            searchBoxRef.current.value = '';
            setSearchTerm('');
        }
    };

    const onChangeHandler = event => {
        setSearchTerm(event.target.value);
    };

    return (
        <>
            <div className='select-box'>
                <div className='options-container' ref={optionsContainer}>
                    {props.data
                        .filter(elem => elem.data.type === 'property')
                        .map((el, i) => {
                            return (
                                <SearchBoxItem
                                    key={i}
                                    searchTerm={searchTerm}
                                    id={el.data.id}
                                    label={el.data.parent}
                                    property={el.data.label}
                                    onItemClickHandler={onItemClickHandler}
                                />
                            );
                        })}
                </div>

                <div
                    className='selected'
                    onClick={searchBoxClicked}
                    onBlur={searchBoxExit}
                >
                    Search ID or property
                </div>

                <div className='search-box'>
                    <input
                        type='text'
                        ref={searchBoxRef}
                        onChange={onChangeHandler}
                        value={searchTerm}
                        placeholder='Enter filter...'
                    />
                </div>
            </div>
        </>
    );
}
