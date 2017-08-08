import React, {Component, PropTypes} from 'react';
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
      this.props.initialVisibleMonth = this.props.initial_visible_month;
      this.props.minDateRange = this.props.min_date_range;
      this.props.maxDateRange = this.props.max_date_range;
      const momentProps = this.convertPropsToMoment(props);
      this.state = {
        date: momentProps.date,
        focused: props.autoFocus,
        initialVisibleMonth: momentProps.initialVisibleMonth,
        minDateRange: momentProps.min,
        maxDateRange: momentProps.max,
        firstInitialVisibleMonth: props.initial_visible_month,
        initialMinDateRange: props.min_date_range,
        initialMaxDateRange: props.max_date_range
      };
    }

    convertPropsToMoment(props) {
      let date = null;
      let initialVisibleMonth = moment(props.date);
      if(typeof props.date !== 'undefined') { date = moment(props.date); }
      if(typeof props.initialVisibleMonth != 'undefined') { initialVisibleMonth = moment(props.initialVisibleMonth); }
      let min, max;
      if(typeof props.minDateRange !== 'undefined' &&
         typeof props.maxDateRange !== 'undefined') {
        min = moment(props.minDateRange);
        max = moment(props.maxDateRange);
      }
      return {date, initialVisibleMonth, min, max}
    }

    componentWillReceiveProps(newProps) {
      let propObj = {
        initialVisibleMonth: newProps.initial_visible_month,
        minDateRange: newProps.min_date_range,
        maxDateRange: newProps.max_date_range
      }
      const momentProps = this.convertPropsToMoment(propObj);
      if (this.props.date != momentProps.date) {
        this.setState({ date: momentProps.date });
      }
      if (this.state.firstInitialVisibleMonth != newProps.initial_visible_month){
        this.setState({
          firstInitialVisibleMonth: newProps.initial_visible_month,
          initialVisibleMonth: momentProps.initialVisibleMonth
        })
      }
      if (this.state.initialMinDateRange != newProps.min_date_range){
        this.setState({
          initialMinDateRange: newProps.min_date_range,
          minDateRange: momentProps.minDateRange
        })
      }
      if (this.state.initialMaxDateRange != newProps.max_date_range){
        this.setState({
          initialMaxDateRange: newProps.max_date_range,
          maxDateRange: momentProps.maxDateRange
        })
      }
    }

    render() {
        const {setProps, fireEvent} = this.props
        return (
          <SingleDatePicker
            date={ this.state.date }
            onDateChange={date => this.setState({ date })}
            onDatesChange={({ date }) => {
              this.setState({ date });
                if (date != null) {
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
            focused={ this.state.focused }
            onFocusChange={({ focused }) => this.setState({ focused })}
            initialVisibleMonth={() => {
              if (this.state.date != null) {
                return this.state.date
              } else {
                return this.state.initialVisibleMonth
              }
            }}
            isOutsideRange={date =>
              date < this.state.minDateRange || date >= this.state.maxDateRange
            }
            numberOfMonths={ this.props.number_of_months_shown }
            withPortal={ this.props.with_portal }
            withFullScreenPortal={ this.props.with_full_screen_portal }
            firstDayOfWeek={ this.props.first_day_of_week }
            enableOutSideDays={ this.props.show_outside_days }
            monthFormat={ this.props.month_format }
            displayFormat={ this.props.display_format }
            placeholder={ this.props.placeholder }
            showClearDate={ this.props.clearable }
            disabled={ this.props.disabled }
            keepOpenOnDateSelect={ this.props.stay_open_on_select }
            reopenPickerOnClearDates={ this.props.reopen_calendar_on_clear }
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
     * Specifies the lowest selectable date for the component,
     * best practice is to pass value via datetime object
     */
    min_date_range: PropTypes.string,

    /**
     * Specifies the highest selectable date for the component,
     * best practice is to pass value via datetime object
     */
    max_date_range: PropTypes.string,

    /**
     * Specifies the date that is initially presented when the user
     * opens the calendar, best practice is to pass value via datetime
     * object
     */
    initial_visible_month: PropTypes.string,

    /**
     * Text that will be displayed in the first input
     * box of the date picker when no date is selected
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
    * If True, calendar will open in a screen overlay portal
    */
    with_portal: PropTypes.bool,

   /**
    * If True, calendar will open in a full screen overlay portal, will
    * take precedent over 'withPortal' if both are set to true
    */
    with_full_screen_portal: PropTypes.bool,

   /**
    * Specifies what day is the first day of the week, values must be
    * from [0, ..., 6]
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
    * valid formats are variations of "MM YY"
    */
   month_format: PropTypes.string,

   /**
    * Specifies the format that the selected dates will be displayed
    * valid formats are variations of "MM YY DD"
    */
   display_format: PropTypes.string,

   /**
    * If True, no dates can be selected.
    */
   disabled: PropTypes.bool,

   /**
    * If True, there will be a button that allows for clearing the dates
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
