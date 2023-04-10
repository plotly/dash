import {memo} from 'react';

function SearchBoxItem({label, property, id, searchTerm, onItemClickHandler}) {
    const matchSearchTerm = () => {
        if (
            label.toLowerCase().indexOf(searchTerm.toLowerCase()) !== -1 ||
            property.toLowerCase().indexOf(searchTerm.toLowerCase()) !== -1
        ) {
            return 'option';
        } else {
            return 'option hidden';
        }
    };

    return (
        <div
            className={matchSearchTerm()}
            data-label={label}
            data-property={property}
            data-id={id}
            onClick={event => onItemClickHandler(event)}
        >
            <div className='searchBoxItem'>
                <span className='id'>{label}</span>
                <span>{property}</span>
            </div>
        </div>
    );
}

export const MemoSearchBoxItem = memo(SearchBoxItem);
