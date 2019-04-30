import 'react-dates/initialize';
import {DateRangePicker} from 'react-dates';
import PropTypes from 'prop-types';
import React, {Component} from 'react';

import convertToMoment from '../utils/convertToMoment';

/**
 * DatePickerRange is a tailor made component designed for selecting
 * timespan across multiple days off of a calendar.
 *
 * The DatePicker integrates well with the Python datetime module with the
 * startDate and endDate being returned in a string format suitable for
 * creating datetime objects.
 *
 * This component is based off of Airbnb's react-dates react component
 * which can be found here: https://github.com/airbnb/react-dates
 */
export default class DatePickerRange extends Component {
    constructor(props) {
        super(props);
        this.propsToState = this.propsToState.bind(this);
        this.onDatesChange = this.onDatesChange.bind(this);
        this.isOutsideRange = this.isOutsideRange.bind(this);
        this.state = {focused: false};
    }

    propsToState(newProps) {
        this.setState({
            start_date: newProps.start_date,
            end_date: newProps.end_date,
        });
    }

    componentWillReceiveProps(newProps) {
        this.propsToState(newProps);
    }

    componentWillMount() {
        this.propsToState(this.props);
    }

    onDatesChange({startDate: start_date, endDate: end_date}) {
        const {setProps, updatemode} = this.props;

        const oldMomentDates = convertToMoment(this.state, [
            'start_date',
            'end_date',
        ]);

        if (start_date && !start_date.isSame(oldMomentDates.start_date)) {
            if (updatemode === 'singledate') {
                setProps({start_date: start_date.format('YYYY-MM-DD')});
            } else {
                this.setState({start_date: start_date.format('YYYY-MM-DD')});
            }
        }

        if (end_date && !end_date.isSame(oldMomentDates.end_date)) {
            if (updatemode === 'singledate') {
                setProps({end_date: end_date.format('YYYY-MM-DD')});
            } else if (updatemode === 'bothdates') {
                setProps({
                    start_date: this.state.start_date,
                    end_date: end_date.format('YYYY-MM-DD'),
                });
            }
        }
    }

    isOutsideRange(date) {
        const {min_date_allowed, max_date_allowed} = this.state;

        return (
            (min_date_allowed && date.isBefore(min_date_allowed)) ||
            (max_date_allowed && date.isAfter(max_date_allowed))
        );
    }

    render() {
        const {focusedInput} = this.state;

        const {
            calendar_orientation,
            clearable,
            day_size,
            disabled,
            display_format,
            end_date_placeholder_text,
            first_day_of_week,
            is_RTL,
            minimum_nights,
            month_format,
            number_of_months_shown,
            reopen_calendar_on_clear,
            show_outside_days,
            start_date_placeholder_text,
            stay_open_on_select,
            with_full_screen_portal,
            with_portal,
            loading_state,
            id,
            style,
            className,
            start_date_id,
            end_date_id,
        } = this.props;

        const {initial_visible_month} = convertToMoment(this.props, [
            'initial_visible_month',
        ]);

        const {start_date, end_date} = convertToMoment(this.state, [
            'start_date',
            'end_date',
        ]);
        const verticalFlag = calendar_orientation !== 'vertical';

        const DatePickerWrapperStyles = {
            position: 'relative',
            display: 'inline-block',
            ...style,
        };

        return (
            <div
                id={id}
                style={DatePickerWrapperStyles}
                className={className}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
            >
                <DateRangePicker
                    daySize={day_size}
                    disabled={disabled}
                    displayFormat={display_format}
                    enableOutsideDays={show_outside_days}
                    endDate={end_date}
                    endDatePlaceholderText={end_date_placeholder_text}
                    firstDayOfWeek={first_day_of_week}
                    focusedInput={focusedInput}
                    initialVisibleMonth={() => {
                        if (initial_visible_month) {
                            return initial_visible_month;
                        } else if (end_date && focusedInput === 'endDate') {
                            return end_date;
                        } else if (start_date && focusedInput === 'startDate') {
                            return start_date;
                        }
                        return start_date;
                    }}
                    isOutsideRange={this.isOutsideRange}
                    isRTL={is_RTL}
                    keepOpenOnDateSelect={stay_open_on_select}
                    minimumNights={minimum_nights}
                    monthFormat={month_format}
                    numberOfMonths={number_of_months_shown}
                    onDatesChange={this.onDatesChange}
                    onFocusChange={focusedInput =>
                        this.setState({focusedInput})
                    }
                    orientation={calendar_orientation}
                    reopenPickerOnClearDates={reopen_calendar_on_clear}
                    showClearDates={clearable}
                    startDate={start_date}
                    startDatePlaceholderText={start_date_placeholder_text}
                    withFullScreenPortal={
                        with_full_screen_portal && verticalFlag
                    }
                    withPortal={with_portal && verticalFlag}
                    startDateId={start_date_id}
                    endDateId={end_date_id}
                />
            </div>
        );
    }
}

DatePickerRange.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Specifies the starting date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    start_date: PropTypes.string,

    /**
     * The HTML element ID of the start date input field.
     * Not used by Dash, only by CSS.
     */
    start_date_id: PropTypes.string,

    /**
     * The HTML element ID of the end date input field.
     * Not used by Dash, only by CSS.
     */
    end_date_id: PropTypes.string,

    /**
     * Specifies the ending date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    end_date: PropTypes.string,

    /**
     * Specifies the lowest selectable date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    min_date_allowed: PropTypes.string,

    /**
     * Specifies the highest selectable date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    max_date_allowed: PropTypes.string,

    /**
     * Specifies the month that is initially presented when the user
     * opens the calendar. Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     *
     */
    initial_visible_month: PropTypes.string,

    /**
     * Text that will be displayed in the first input
     * box of the date picker when no date is selected. Default value is 'Start Date'
     */
    start_date_placeholder_text: PropTypes.string,

    /**
     * Text that will be displayed in the second input
     * box of the date picker when no date is selected. Default value is 'End Date'
     */
    end_date_placeholder_text: PropTypes.string,

    /**
     * Size of rendered calendar days, higher number
     * means bigger day size and larger calendar overall
     */
    day_size: PropTypes.number,

    /**
     * Orientation of calendar, either vertical or horizontal.
     * Valid options are 'vertical' or 'horizontal'.
     */
    calendar_orientation: PropTypes.oneOf(['vertical', 'horizontal']),

    /**
     * Determines whether the calendar and days operate
     * from left to right or from right to left
     */
    is_RTL: PropTypes.bool,

    /**
     * If True, the calendar will automatically open when cleared
     */
    reopen_calendar_on_clear: PropTypes.bool,

    /**
     * Number of calendar months that are shown when calendar is opened
     */
    number_of_months_shown: PropTypes.number,

    /**
     * If True, calendar will open in a screen overlay portal,
     * not supported on vertical calendar
     */
    with_portal: PropTypes.bool,

    /**
     * If True, calendar will open in a full screen overlay portal, will
     * take precedent over 'withPortal' if both are set to true,
     * not supported on vertical calendar
     */
    with_full_screen_portal: PropTypes.bool,

    /**
     * Specifies what day is the first day of the week, values must be
     * from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday
     */
    first_day_of_week: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),

    /**
     * Specifies a minimum number of nights that must be selected between
     * the startDate and the endDate
     */
    minimum_nights: PropTypes.number,

    /**
     * If True the calendar will not close when the user has selected a value
     * and will wait until the user clicks off the calendar
     */
    stay_open_on_select: PropTypes.bool,

    /**
     * If True the calendar will display days that rollover into
     * the next month
     */
    show_outside_days: PropTypes.bool,

    /**
     * Specifies the format that the month will be displayed in the calendar,
     * valid formats are variations of "MM YY". For example:
     * "MM YY" renders as '05 97' for May 1997
     * "MMMM, YYYY" renders as 'May, 1997' for May 1997
     * "MMM, YY" renders as 'Sep, 97' for September 1997
     */
    month_format: PropTypes.string,

    /**
     * Specifies the format that the selected dates will be displayed
     * valid formats are variations of "MM YY DD". For example:
     * "MM YY DD" renders as '05 10 97' for May 10th 1997
     * "MMMM, YY" renders as 'May, 1997' for May 10th 1997
     * "M, D, YYYY" renders as '07, 10, 1997' for September 10th 1997
     * "MMMM" renders as 'May' for May 10 1997
     */
    display_format: PropTypes.string,

    /**
     * If True, no dates can be selected.
     */
    disabled: PropTypes.bool,

    /**
     * Whether or not the dropdown is "clearable", that is, whether or
     * not a small "x" appears on the right of the dropdown that removes
     * the selected value.
     */
    clearable: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

    /**
     * CSS styles appended to wrapper div
     */
    style: PropTypes.object,

    /**
     * Appends a CSS class to the wrapper div component.
     */
    className: PropTypes.string,

    /**
     * Determines when the component should update
     * its value. If `bothdates`, then the DatePicker
     * will only trigger its value when the user has
     * finished picking both dates. If `singledate`, then
     * the DatePicker will update its value
     * as one date is picked.
     */
    updatemode: PropTypes.oneOf(['singledate', 'bothdates']),

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),
};

DatePickerRange.defaultProps = {
    calendar_orientation: 'horizontal',
    is_RTL: false,
    day_size: 39,
    with_portal: false,
    with_full_screen_portal: false,
    first_day_of_week: 0,
    number_of_months_shown: 1,
    stay_open_on_select: false,
    reopen_calendar_on_clear: false,
    clearable: false,
    disabled: false,
    updatemode: 'singledate',
};
