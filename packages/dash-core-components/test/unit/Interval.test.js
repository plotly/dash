import Interval from '../../src/components/Interval.react.js';
import React, {cloneElement, Component} from 'react';
import PropTypes from 'prop-types';
import omit from 'lodash/omit';
import {mount, render} from 'enzyme';

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

    render() {
        return cloneElement(this.props.children, {
            ...omit(this.props, ['children']),
            n_intervals: this.state.n_intervals,
            setProps: this.setProps,
        });
    }
}

IntervalWrapper.propTypes = {
    children: PropTypes.node,
    setProps: PropTypes.func,
};

const intervalLength = 50;

// The following number should be large enough for any
// outstanding timeout events to have settled, but still
// small enough to be unnoticeable by our implementation.
const intervalNegligibleMargin = intervalLength / 5;

describe('Basic interval usage', () => {
    const makeSut = () => {
        const results = {
            nIntervals: 0,
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
            <IntervalWrapper setProps={setProps}>
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
            }, intervalLength + intervalNegligibleMargin);
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
                    : null,
            });
        }
    }

    DelayedSetPropsWrapper.propTypes = {
        children: PropTypes.node,
        setProps: PropTypes.func,
    };

    const makeSut = () => {
        const results = {
            nIntervals: 0,
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
            <DelayedSetPropsWrapper setProps={setProps}>
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
            }, intervalLength + intervalNegligibleMargin);
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

    DisabledTestingIntervalWrapper.propTypes = {
        children: PropTypes.node,
        setProps: PropTypes.func,
        handleInterval: PropTypes.func,
    };

    const makeSut = handleInterval => {
        const results = {
            nIntervals: 0,
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
                }, intervalLength + intervalNegligibleMargin);
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
                }, intervalLength + intervalNegligibleMargin);
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
