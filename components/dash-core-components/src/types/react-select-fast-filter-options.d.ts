declare module 'react-select-fast-filter-options' {
  interface FilterOption {
    [key: string]: any;
    label?: string;
    value?: any;
  }

  interface CreateFilterOptionsConfig {
    /**
     * Array of property names to index for searching.
     * If not provided, defaults to the labelKey.
     */
    indexes?: string[];

    /**
     * The indexing strategy from js-search library.
     * Defaults to AllSubstringsIndexStrategy.
     */
    indexStrategy?: any;

    /**
     * The property name used for labels.
     * @default 'label'
     */
    labelKey?: string;

    /**
     * The array of options to filter.
     * @default []
     */
    options?: FilterOption[];

    /**
     * Text sanitizer function from js-search library.
     */
    sanitizer?: any;

    /**
     * Search index implementation from js-search library.
     */
    searchIndex?: any;

    /**
     * Tokenizer function from js-search library.
     */
    tokenizer?: {
      tokenize(text: string): string[];
    };

    /**
     * The property name used for values.
     * @default 'value'
     */
    valueKey?: string;
  }

  type FilterOptionsFunction = (
    options: FilterOption[],
    filter: string,
    selectedOptions?: FilterOption[]
  ) => FilterOption[];

  /**
   * Creates a fast filter function optimized for filtering large option lists.
   *
   * @param config Configuration object for the filter function
   * @returns A filter function that can be used to filter options
   */
  function createFilterOptions(config: CreateFilterOptionsConfig): FilterOptionsFunction;

  export default createFilterOptions;
}
