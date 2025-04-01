import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

const RenderType = (props) => {
    const onClick = () => {
        props.setProps({n_clicks: (props.n_clicks || 0) + 1})
    }

    return <div id={props.id}>
        <span>{props.dashRenderType}</span>
        <button onClick={onClick}>Test Internal</button>
    </div>;
};

RenderType.propTypes = {
    id: PropTypes.string,
    dashRenderType: PropTypes.string,
    n_clicks: PropTypes.number,
    setProps: PropTypes.func
};

RenderType.dashRenderType = true;
export default RenderType;
