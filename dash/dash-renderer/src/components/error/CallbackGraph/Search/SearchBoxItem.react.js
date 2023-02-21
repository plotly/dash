export function SearchBoxItem({
    label,
    property,
    id,
    searchTerm,
    onItemClickHandler
}) {
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
            <div className='tester'>
                <span className='title animated fadeIn id'>{label}</span>
                <span className='title animated fadeIn'>{property}</span>
            </div>
        </div>
    );
}
