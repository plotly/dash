import Interval from '../../src/components/Interval.react.js';
import React, {cloneElement, Component} from 'react';
import omit from 'lodash/omit';
import {mount, shallow, render} from 'enzyme';

test('Interval render', () => {
    const interval = render(<Interval />);

    expect(interval.html()).toBeNull();
});

class IntervalWrapper extends Component {
    constructor(props) {
        super(props);
        this.state = {
            n_intervals: 0,
        };
        this.setProps = this.setProps.bind(this);
    }

    setProps({n_intervals}) {
        this.setState(
            {
                n_intervals,
            },
            () => {
                if (this.props.setProps) {
                    this.props.setProps({n_intervals});
                }
            }
        );
    }

    fireEvent({event}) {
        this.props.fireEvent({event});
    }

    render() {
        return cloneElement(this.props.children, {
            ...omit(this.props, ['children']),
            n_intervals: this.state.n_intervals,
            setProps: this.setProps,
        });
    }
}

const intervalLength = 50;

// The following number should be large enough for any
// outstanding timeout events to have settled, but still
// small enough to be unnoticeable by our implementation.
const intervalNegligibleMargin = intervalLength * 0.2;

describe('Basic interval usage', () => {
    const makeSut = () => {
        const results = {
            fireEventCalls: 0,
            nIntervals: 0,
        };

        const fireEvent = ({event}) => {
            if (event === 'interval') {
                results.fireEventCalls += 1;
            }
        };

        const setProps = props => {
            if ('n_intervals' in props) {
                results.nIntervals = props.n_intervals;
            }
        };

        const defaultProps = {
            id: 'test-interval',
            interval: intervalLength,
        };

        const wrapper = mount(
            <IntervalWrapper fireEvent={fireEvent} setProps={setProps}>
                <Interval {...defaultProps} />
            </IntervalWrapper>
        );
        const interval = wrapper.childAt(0);

        return {interval, results};
    };

    test('props.id =>', () => {
        const {interval} = makeSut();
        expect(interval.props().id).toEqual('test-interval');
    });

    describe('t = 0', () => {
        test('n_intervals = 0', () => {
            const {results} = makeSut();
            expect(results.nIntervals).toEqual(0);
        });
    });

    describe('After 1 interval elapsed', () => {
        test('n_intervals = 1', done => {
            const {results} = makeSut();
            setTimeout(() => {
                expect(results.nIntervals).toEqual(1);
                done();
            }, intervalLength * 1 + intervalNegligibleMargin);
        });
    });

    describe('After 2 intervals elapsed', () => {
        test('n_intervals = 2', done => {
            const {results} = makeSut();
            setTimeout(() => {
                expect(results.nIntervals).toEqual(2);
                done();
            }, intervalLength * 2 + intervalNegligibleMargin);
        });
    });
});

describe('Delayed setProps provisioning', () => {
    class DelayedSetPropsWrapper extends Component {
        constructor(props) {
            super(props);
            this.state = {
                setPropsProvided: false,
            };
        }

        componentDidMount() {
            this.setState({
                setPropsProvided: true,
            });
        }

        render() {
            return cloneElement(this.props.children, {
                ...omit(this.props, ['children']),
                setProps: this.state.setPropsProvided
                    ? this.props.setProps
                    : undefined,
            });
        }
    }

    const makeSut = () => {
        const results = {
            fireEventCalls: 0,
            nIntervals: 0,
        };

        const fireEvent = ({event}) => {
            if (event === 'interval') {
                results.fireEventCalls += 1;
            }
        };

        const setProps = props => {
            if ('n_intervals' in props) {
                results.nIntervals = props.n_intervals;
            }
        };

        const defaultProps = {
            id: 'test-interval',
            interval: intervalLength,
        };

        const wrapper = mount(
            <DelayedSetPropsWrapper fireEvent={fireEvent} setProps={setProps}>
                <IntervalWrapper>
                    <Interval {...defaultProps} />
                </IntervalWrapper>
            </DelayedSetPropsWrapper>
        );
        const interval = wrapper.childAt(0).childAt(0);

        return {interval, results};
    };

    test('props.id =>', () => {
        const {interval} = makeSut();
        expect(interval.props().id).toEqual('test-interval');
    });

    describe('t = 0', () => {
        test('n_intervals = 0', () => {
            const {results} = makeSut();
            expect(results.nIntervals).toEqual(0);
        });
    });

    describe('After 1 interval elapsed', () => {
        test('n_intervals = 1', done => {
            const {results} = makeSut();
            setTimeout(() => {
                expect(results.nIntervals).toEqual(1);
                done();
            }, intervalLength * 1 + intervalNegligibleMargin);
        });
    });

    describe('After 2 intervals elapsed', () => {
        test('n_intervals = 2', done => {
            const {results} = makeSut();
            setTimeout(() => {
                expect(results.nIntervals).toEqual(2);
                done();
            }, intervalLength * 2 + intervalNegligibleMargin);
        });
    });
});

describe('Usage of disabled = true', () => {
    class DisabledTestingIntervalWrapper extends Component {
        constructor(props) {
            super(props);
            this.state = {
                disabled: false,
            };
            this.setProps = this.setProps.bind(this);
        }

        setProps({n_intervals}) {
            this.props.setProps({n_intervals});
            if (this.props.handleInterval) {
                this.props.handleInterval(
                    n_intervals,
                    this.setState.bind(this)
                );
            }
        }

        render() {
            return cloneElement(this.props.children, {
                ...omit(this.props, ['children']),
                disabled: this.state.disabled,
                setProps: this.setProps,
            });
        }
    }

    const makeSut = handleInterval => {
        const results = {
            fireEventCalls: 0,
            nIntervals: 0,
        };

        const fireEvent = ({event}) => {
            if (event === 'interval') {
                results.fireEventCalls += 1;
            }
        };

        const setProps = props => {
            if ('n_intervals' in props) {
                results.nIntervals = props.n_intervals;
            }
        };

        const defaultProps = {
            id: 'test-interval',
            interval: intervalLength,
        };

        const wrapper = mount(
            <DisabledTestingIntervalWrapper
                handleInterval={handleInterval}
                setProps={setProps}
                fireEvent={fireEvent}
            >
                <IntervalWrapper>
                    <Interval {...defaultProps} />
                </IntervalWrapper>
            </DisabledTestingIntervalWrapper>
        );
        const interval = wrapper.childAt(0).childAt(0);

        return {interval, results};
    };

    describe('disabling permanently after one interval', () => {
        const handleInterval = (intervalsElapsed, setState) => {
            // disable after one interval
            if (intervalsElapsed === 1) {
                setState({
                    disabled: true,
                });
            }
        };

        describe('t = 0', () => {
            test('n_intervals = 0', () => {
                const {results} = makeSut(handleInterval);
                expect(results.nIntervals).toEqual(0);
            });
        });

        describe('After 1 interval elapsed', () => {
            test('n_intervals = 1', done => {
                const {results} = makeSut(handleInterval);
                setTimeout(() => {
                    expect(results.nIntervals).toEqual(1);
                    done();
                }, intervalLength * 1 + intervalNegligibleMargin);
            });
        });

        describe('After 2 intervals elapsed', () => {
            test('n_intervals = 1', done => {
                const {results} = makeSut(handleInterval);
                setTimeout(() => {
                    expect(results.nIntervals).toEqual(1);
                    done();
                }, intervalLength * 2 + intervalNegligibleMargin);
            });
        });

        describe('After 3 intervals elapsed', () => {
            test('n_intervals = 1', done => {
                const {results} = makeSut(handleInterval);
                setTimeout(() => {
                    expect(results.nIntervals).toEqual(1);
                    done();
                }, intervalLength * 3 + intervalNegligibleMargin);
            });
        });
    });

    describe('disabling temporarily for one interval', () => {
        const handleInterval = (intervalsElapsed, setState) => {
            // disable after one interval, just before the next
            if (intervalsElapsed === 1) {
                setTimeout(() => {
                    setState(
                        {
                            disabled: true,
                        },
                        () => {
                            // re-enable one interval later
                            setTimeout(() => {
                                setState({
                                    disabled: false,
                                });
                            }, intervalLength);
                        }
                    );
                }, intervalLength - intervalNegligibleMargin);
            }
        };

        describe('t = 0', () => {
            test('n_intervals = 0', () => {
                const {results} = makeSut(handleInterval);
                expect(results.nIntervals).toEqual(0);
            });
        });

        describe('After 1 interval elapsed', () => {
            test('n_intervals = 1', done => {
                const {results} = makeSut(handleInterval);
                setTimeout(() => {
                    expect(results.nIntervals).toEqual(1);
                    done();
                }, intervalLength * 1 + intervalNegligibleMargin);
            });
        });

        describe('After 2 intervals elapsed', () => {
            test('n_intervals = 1', done => {
                const {results} = makeSut(handleInterval);
                setTimeout(() => {
                    expect(results.nIntervals).toEqual(1);
                    done();
                }, intervalLength * 2 + intervalNegligibleMargin);
            });
        });

        describe('After 3 intervals elapsed', () => {
            test('n_intervals = 2', done => {
                const {results} = makeSut(handleInterval);
                setTimeout(() => {
                    expect(results.nIntervals).toEqual(2);
                    done();
                }, intervalLength * 3 + intervalNegligibleMargin);
            });
        });
    });
});
