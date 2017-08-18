import React, { Component, PropTypes } from 'react';
import { SingleDatePicker } from 'react-dates';
import moment from 'moment';

/**
 * DatePickerRange is a tailor made component designed for selecting
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
  constructor(props) {
    super(props);
    const propObj = {
      date: this.props.date,
      initialVisibleMonth: this.props.initial_visible_month,
      minDateAllowed: this.props.min_date_allowed,
      maxDateAllowed: this.props.max_date_allowed
    };
    const momentProps = this.convertPropsToMoment(propObj);
    this.state = {
      date: momentProps.date,
      focused: props.autoFocus,
      initialVisibleMonth: momentProps.initialVisibleMonth,
      minDateAllowed: momentProps.min,
      maxDateAllowed: momentProps.max,
      prevInitialVisibleMonth: props.initial_visible_month,
      prevMinDateAllowed: props.min_date_allowed,
      prevMaxDateAllowed: props.max_date_allowed
    };
  }

  convertPropsToMoment(props) {
    let date = null;
    let initialVisibleMonth = moment(props.date);
    if (typeof props.date !== 'undefined') {
      date = moment(props.date);
    }

    if (typeof props.initialVisibleMonth !== 'undefined') {
      initialVisibleMonth = moment(props.initialVisibleMonth);
    }

    let min; let max;
    if (typeof props.minDateAllowed !== 'undefined') {
      min = moment(props.minDateAllowed);
    }

    if (typeof props.maxDateAllowed !== 'undefined') {
      max = moment(props.maxDateAllowed);
      max.add(1, 'days');
    }

    return { date, initialVisibleMonth, min, max };
  }

  componentWillReceiveProps(newProps) {
    const propObj = {
      date: newProps.date,
      initialVisibleMonth: newProps.initial_visible_month,
      minDateAllowed: newProps.min_date_allowed,
      maxDateAllowed: newProps.max_date_allowed
    };
    const momentProps = this.convertPropsToMoment(propObj);
    if (this.state.date !== momentProps.date) {
      this.setState({ date: momentProps.date });
    }

    if (this.state.prevInitialVisibleMonth !== newProps.initial_visible_month) {
      this.setState({
          prevInitialVisibleMonth: newProps.initial_visible_month,
          initialVisibleMonth: momentProps.initialVisibleMonth
        });
    }

    if (this.state.prevMinDateAllowed !== newProps.min_date_allowed) {
      this.setState({
        prevMinDateAllowed: newProps.min_date_allowed,
        minDateAllowed: momentProps.minDateAllowed
      });
    }

    if (this.state.prevMaxDateAllowed !== newProps.max_date_allowed) {
      this.setState({
        prevMaxDateAllowed: newProps.max_date_allowed,
        maxDateAllowed: momentProps.maxDateAllowed
      });
    }
  }

  render() {
    const { setProps, fireEvent } = this.props;
    let verticalFlag = true;
    if (this.props.calendar_orientation === 'vertical') {
      verticalFlag = false;
    }

    return (
      <SingleDatePicker
        date={this.state.date}
        onDateChange={(date) => {
            this.setState({ date });
            if (date !== null) {
              const dateStr = date.format('YYYY-MM-DD');
              if (setProps) {
                setProps({
                  date: dateStr
                });
              }
              if (fireEvent) {
                fireEvent('change');
              }
            }
          }
        }
        focused={this.state.focused}
        onFocusChange={({ focused }) => this.setState({ focused })}
        initialVisibleMonth={() => {
          if (this.state.date !== null) {
            return this.state.date;
          } else {
            return this.state.initialVisibleMonth;
          }
        }
        }
        isOutsideRange={(date) => {
          if (typeof this.state.minDateAllowed !== 'undefined' &&
              typeof this.state.maxDateAllowed !== 'undefined') {
            return date < this.state.minDateAllowed || date >= this.state.maxDateAllowed;
          } else if (typeof this.state.minDateAllowed === 'undefined' &&
                     typeof this.state.maxDateAllowed !== 'undefined') {
            return date >= this.state.maxDateAllowed;
          } else if (typeof this.state.minDateAllowed !== 'undefined' &&
                     typeof this.state.maxDateAllowed === 'undefined') {
            return date < this.state.minDateAllowed;
          } else {
            return false;
          }
        }
        }
        numberOfMonths={this.props.number_of_months_shown}
        withPortal={this.props.with_portal && verticalFlag}
        withFullScreenPortal={this.props.with_full_screen_portal && verticalFlag}
        firstDayOfWeek={this.props.first_day_of_week}
        enableOutSideDays={this.props.show_outside_days}
        monthFormat={this.props.month_format}
        displayFormat={this.props.display_format}
        placeholder={this.props.placeholder}
        showClearDate={this.props.clearable}
        disabled={this.props.disabled}
        keepOpenOnDateSelect={this.props.stay_open_on_select}
        reopenPickerOnClearDates={this.props.reopen_calendar_on_clear}
        isRTL={this.props.is_RTL}
        orientation={this.props.calendar_orientation}
        daySize={this.props.day_size}
      />
    );
  }
}

DatePickerSingle.propTypes = {
    id: PropTypes.string,

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
     * Specifies the month that is initially presented when the user
     * opens the calendar. Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     *
     */
    initial_visible_month: PropTypes.string,

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
     * Text that will be displayed in the input
     * box of the date picker when no date is selected.
     * Default value is 'Start Date'
     */
    placeholder: PropTypes.string,

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
    * take precedent over 'withPortal' if both are set to True,
    * not supported on vertical calendar
    */
    with_full_screen_portal: PropTypes.bool,

    /**
     * Specifies what day is the first day of the week, values must be
     * from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday
     */
    first_day_of_week: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),

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
    dashEvents: PropTypes.oneOf(['change'])
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
  disabled: false
};
