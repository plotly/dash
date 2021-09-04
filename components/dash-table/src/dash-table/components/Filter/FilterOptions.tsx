import React from 'react';

import {FilterCase, IFilterOptions} from 'dash-table/components/Table/props';

interface IFilterCaseButtonProps {
    filterOptions: IFilterOptions;
    toggleFilterOptions: () => void;
}

export default ({
    filterOptions,
    toggleFilterOptions
}: IFilterCaseButtonProps) => (
    <input
        type='button'
        className={`dash-filter--case ${
            filterOptions.case === FilterCase.Sensitive
                ? 'dash-filter--case--sensitive'
                : 'dash-filter--case--insensitive'
        }`}
        onClick={toggleFilterOptions}
        title='Toggle filter case sensitivity'
        value='Aa'
    />
);
