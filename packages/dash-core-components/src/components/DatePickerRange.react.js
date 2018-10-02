import {DateRangePicker} from 'react-dates';
import moment from 'moment';
import PropTypes from 'prop-types';
import R from 'ramda';
import React, {Component} from 'react';

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
    constructor() {
        super();
        this.propsToState = this.propsToState.bind(this);
        this.onDatesChange = this.onDatesChange.bind(this);
        this.isOutsideRange = this.isOutsideRange.bind(this);
    }

    propsToState(newProps) {
        /*
         * state includes:
         * - user modifiable attributes
         * - moment converted attributes
         */
        const newState = {};
        const momentProps = [
            'start_date',
            'end_date',
            'initial_visible_month',
            'max_date_allowed',
            'min_date_allowed',
        ];
        momentProps.forEach(prop => {
            if (R.type(newProps[prop]) !== 'Undefined') {
                newState[prop] = moment(newProps[prop]);
            }
            if (prop === 'max_date_allowed' && R.has(prop, newState)) {
                newState[prop].add(1, 'days');
            }
        });
        this.setState(newState);
    }

    componentWillReceiveProps(newProps) {
        this.propsToState(newProps);
    }

    componentWillMount() {
        this.propsToState(this.props);
    }
    onDatesChange({startDate: start_date, endDate: end_date}) {
        const {setProps, fireEvent, updatemode} = this.props;
        const old_start_date = this.state.start_date;
        const old_end_date = this.state.end_date;
        const newState = {};
        if (setProps && start_date !== null && start_date !== old_start_date) {
            if (updatemode === 'singledate') {
                setProps({start_date: start_date.format('YYYY-MM-DD')});
            }
        }

        newState.start_date = start_date;

        if (setProps && end_date !== null && end_date !== old_end_date) {
            if (updatemode === 'singledate') {
                setProps({end_date: end_date.format('YYYY-MM-DD')});
            } else if (updatemode === 'bothdates') {
                setProps({
                    start_date: start_date.format('YYYY-MM-DD'),
                    end_date: end_date.format('YYYY-MM-DD'),
                });
            }
        }
        newState.end_date = end_date;

        if (fireEvent) {
            fireEvent('change');
        }

        this.setState(newState);
    }

    isOutsideRange(date) {
        const {min_date_allowed, max_date_allowed} = this.state;
        const notUndefined = R.complement(
            R.pipe(
                R.type,
                R.equals('Undefined')
            )
        );
        return (
            (notUndefined(min_date_allowed) && date < min_date_allowed) ||
            (notUndefined(max_date_allowed) && date >= max_date_allowed)
        );
    }

    render() {
        const {
            start_date,
            end_date,
            focusedInput,
            initial_visible_month,
        } = this.state;

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
        } = this.props;

        const verticalFlag = calendar_orientation !== 'vertical';

        return (
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
                    }
                    if (focusedInput === 'endDate') {
                        return end_date;
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
                onFocusChange={focusedInput => this.setState({focusedInput})}
                orientation={calendar_orientation}
                reopenPickerOnClearDates={reopen_calendar_on_clear}
                showClearDates={clearable}
                startDate={start_date}
                startDatePlaceholderText={start_date_placeholder_text}
                withFullScreenPortal={with_full_screen_portal && verticalFlag}
                withPortal={with_portal && verticalFlag}
            />
        );
    }
}

DatePickerRange.propTypes = {
    id: PropTypes.string,

    /**
     * Specifies the starting date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    start_date: PropTypes.string,

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
     * Dash-assigned callback that gets fired when the value changes.
     */
    dashEvents: PropTypes.oneOf(['change']),

    /**
     * Determines when the component should update
     * its value. If `bothdates`, then the DatePicker
     * will only trigger its value when the user has
     * finished picking both dates. If `singledate`, then
     * the DatePicker will update its value
     * as one date is picked.
     */
    updatemode: PropTypes.oneOf(['singledate', 'bothdates']),

    fireEvent: PropTypes.func,
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
