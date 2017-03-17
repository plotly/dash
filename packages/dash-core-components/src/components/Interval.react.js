import React, {Component, PropTypes} from 'react'; // eslint-disable-line no-unused-vars

export default class Interval extends Component {
    constructor(props) {
        super(props);
        this.state = {};
        this.setInterval = this.setInterval.bind(this);
    }

    setInterval(props) {
        const {interval, fireEvent} = props;
        this.setState({
            intervalId: window.setInterval(function intervalFunction(){
                if (fireEvent) {
                    fireEvent({event: 'setInterval'});
                }
            }, interval)
        });
    }

    componentDidMount() {
        if (this.props.fireEvent) {
            this.setInterval(this.props);
        }
    }

    componentWillReceiveProps(nextProps) {
        if (!this.props.fireEvent && nextProps.fireEvent) {
            this.setInterval(nextProps);
        } else if (
            !this.props.interval !== nextProps.interval &&
            this.state.intervalId
        ) {
            window.clearInterval(this.state.intervalId);
            this.setInterval(nextProps);
        }
    }

    componentWillUnmount() {
        window.clearInterval(this.state.intervalId);
    }

    render() {
        return null;
    }
}

Interval.propTypes = {
    /**
     * This component will fire an event every `interval`
     * milliseconds with the event name `setInterval`
     */
    interval: PropTypes.number,

    /**
     * Dash assigned callback
     */
    fireEvent: PropTypes.function,

    /**
     * Dash assigned callback
     */
    setProps: PropTypes.function
};

Interval.defaultProps = {
    interval: 1000
};
