import React from 'react'
import "./CollapseExpand.scss";

const CollapseExpand = (props) => {
	return (
		<div className={["collapse-expand", props.collapsed ? "collapsed" : "expand"].join(' ')}>
            {props.children}
		</div>
	);
};

CollapseExpand.defaultProps = {
	collapsed: false,
};

export default CollapseExpand;
