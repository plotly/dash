import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

const DrawCounter = (props) => {
    const [count, setCount] = useState(0);
    useEffect(() => {
        setCount(count + 1);
    }, [props]);
    return <div id={props.id}>{count}</div>;
};

DrawCounter.propTypes = {
    id: PropTypes.string,
};
export default DrawCounter;
