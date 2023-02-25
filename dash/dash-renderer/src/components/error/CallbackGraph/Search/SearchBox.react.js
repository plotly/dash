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

        props.onSearchBarClicked();
        props.onSelectionChanged(event);
    };

    useEffect(() => {
        if (props.active) {
            optionsContainer.current.classList.add('active');
            searchBoxRef.current.focus();
            searchBoxRef.current.value = '';
        } else {
            optionsContainer.current.classList.remove('active');
            searchBoxRef.current.blur();
            searchBoxRef.current.value = '';
            setSearchTerm('');
        }
    }, [props.active]);

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

                <div className='selected' onClick={props.onSearchBarClicked}>
                    Search ID or property
                </div>

                <div className='search-box'>
                    <input
                        id='searchBoxInput'
                        type='text'
                        className='mousetrap'
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
