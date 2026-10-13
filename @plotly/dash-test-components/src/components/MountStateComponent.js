import React, {useEffect} from "react";
import PropTypes from "prop-types";

// A component that establishes its own initial state on mount by calling
// setProps - the same pattern dbc Tabs uses to pick its default active_tab
// (#3929). Used to guard against the first-render resetComponentState wiping
// that mount-time update before it takes effect.
const MountStateComponent = ({id, setProps, value = "initial"}) => {
    useEffect(() => {
        setProps({value: "mounted"});
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    return <div id={id}>{value}</div>;
};

MountStateComponent.propTypes = {
    id: PropTypes.string,
    value: PropTypes.string,
    setProps: PropTypes.func,
};

export default MountStateComponent;
