import PropTypes from 'prop-types';
import React, {Component, lazy, Suspense} from 'react';
import datePickerSingle from '../utils/LazyLoader/datePickerSingle';
import transformDate from '../utils/DatePickerPersistence';

const RealDateSingleRange = lazy(datePickerSingle);

/**
 * DatePickerSingle is a tailor made component designed for selecting
 * a single day off of a calendar.
 *
 * The DatePicker integrates well with the Python datetime module with the
 * startDate and endDate being returned in a string format suitable for
 * creating datetime objects.
 *
 * This component is based off of Airbnb's react-dates react component
 * which can be found here: https://github.com/airbnb/react-dates
 */
export default class DatePickerSingle extends Component {
    render() {
        return (
            <Suspense fallback={null}>
                <RealDateSingleRange {...this.props} />
            </Suspense>
        );
    }
}

DatePickerSingle.propTypes = {
    /**
     * Specifies the starting date for the component, best practice is to pass
     * value via datetime object
     */
    date: PropTypes.string,

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
     * Specifies additional days between min_date_allowed and max_date_allowed
     * that should be disabled. Accepted datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    disabled_days: PropTypes.arrayOf(PropTypes.string),

    /**
     * Text that will be displayed in the input
     * box of the date picker when no date is selected.
     * Default value is 'Start Date'
     */
    placeholder: PropTypes.string,

    /**
     * Specifies the month that is initially presented when the user
     * opens the calendar. Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     *
     */
    initial_visible_month: PropTypes.string,

    /**
     * Whether or not the dropdown is "clearable", that is, whether or
     * not a small "x" appears on the right of the dropdown that removes
     * the selected value.
     */
    clearable: PropTypes.bool,

    /**
     * If True, the calendar will automatically open when cleared
     */
    reopen_calendar_on_clear: PropTypes.bool,

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
     * Specifies the format that the month will be displayed in the calendar,
     * valid formats are variations of "MM YY". For example:
     * "MM YY" renders as '05 97' for May 1997
     * "MMMM, YYYY" renders as 'May, 1997' for May 1997
     * "MMM, YY" renders as 'Sep, 97' for September 1997
     */
    month_format: PropTypes.string,

    /**
     * Specifies what day is the first day of the week, values must be
     * from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday
     */
    first_day_of_week: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),

    /**
     * If True the calendar will display days that rollover into
     * the next month
     */
    show_outside_days: PropTypes.bool,

    /**
     * If True the calendar will not close when the user has selected a value
     * and will wait until the user clicks off the calendar
     */
    stay_open_on_select: PropTypes.bool,

    /**
     * Orientation of calendar, either vertical or horizontal.
     * Valid options are 'vertical' or 'horizontal'.
     */
    calendar_orientation: PropTypes.oneOf(['vertical', 'horizontal']),

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
     * take precedent over 'withPortal' if both are set to True,
     * not supported on vertical calendar
     */
    with_full_screen_portal: PropTypes.bool,

    /**
     * Size of rendered calendar days, higher number
     * means bigger day size and larger calendar overall
     */
    day_size: PropTypes.number,

    /**
     * Determines whether the calendar and days operate
     * from left to right or from right to left
     */
    is_RTL: PropTypes.bool,

    /**
     * If True, no dates can be selected.
     */
    disabled: PropTypes.bool,

    /**
     * CSS styles appended to wrapper div
     */
    style: PropTypes.object,

    /**
     * Appends a CSS class to the wrapper div component.
     */
    className: PropTypes.string,

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

    /**
     * Used to allow user interactions in this component to be persisted when
     * the component - or the page - is refreshed. If `persisted` is truthy and
     * hasn't changed from its previous value, a `date` that the user has
     * changed while using the app will keep that change, as long as
     * the new `date` also matches what was given originally.
     * Used in conjunction with `persistence_type`.
     */
    persistence: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.string,
        PropTypes.number,
    ]),

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page. Since only `date` is allowed this prop can
     * normally be ignored.
     */
    persisted_props: PropTypes.arrayOf(PropTypes.oneOf(['date'])),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

DatePickerSingle.persistenceTransforms = {
    date: transformDate,
};

DatePickerSingle.defaultProps = {
    calendar_orientation: 'horizontal',
    is_RTL: false,
    day_size: 39,
    with_portal: false,
    with_full_screen_portal: false,
    show_outside_days: true,
    first_day_of_week: 0,
    number_of_months_shown: 1,
    stay_open_on_select: false,
    reopen_calendar_on_clear: false,
    clearable: false,
    disabled: false,
    persisted_props: ['date'],
    persistence_type: 'local',
    disabled_days: [],
};

export const propTypes = DatePickerSingle.propTypes;
export const defaultProps = DatePickerSingle.defaultProps;
