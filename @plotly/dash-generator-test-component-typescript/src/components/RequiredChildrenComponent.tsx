import React from 'react';
import { RequiredChildrenComponentProps } from "../props";


const RequiredChildrenComponent = (props: RequiredChildrenComponentProps) => {
  const {children} = props;
  return (
    <div>
      {children}
    </div>
  )
}

export default RequiredChildrenComponent;
