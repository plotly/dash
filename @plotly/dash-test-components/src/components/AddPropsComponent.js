import React from "react";
import PropTypes from "prop-types";

const AddPropsComponent = (props) => {
    const {children, id} = props;


    return (
        <div id={id}>
            {React.cloneElement(children, {
                receive: `Element #${id} pass`,
                id: id,
            })}
        </div>
    );
};

AddPropsComponent.propTypes = {
    id: PropTypes.string,
    children: PropTypes.node,
};

export default AddPropsComponent;
