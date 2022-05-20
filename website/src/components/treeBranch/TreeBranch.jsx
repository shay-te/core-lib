import React from "react";
import { useState } from "react";
import "./TreeBranch.scss";
import HoverVisible from "../hoverVisible/HoverVisible";
import { useSelector } from "react-redux";


const TreeBranch = (props) => {
	const [visible, setVisible] = useState(false);
	const treeSelected = useSelector((state) => state.treeData.treeSelected);
	
	
	return (
		<div
			onMouseEnter={() => setVisible(true)}
			onMouseLeave={() => setVisible(false)}
			onMouseOver={() => setVisible(true)}
			onClick={props.onBranchClick.bind(this, props.path)}
			className={["tree-branch", treeSelected[props.path]? "selected" : ""].join(" ")}
		>
			<div
				className="branch-title-icon"
				onClick={props.onTitleClick.bind(this, props.path)}
			>
				<div>{props.icon}</div>
				<div className="branch-title">{props.title}</div>
			</div>
			<HoverVisible isVisible={visible}>
				<div
					onClick={props.onImageClick.bind(this, props.path)}
					className={["hover-img"].join(" ")}
				>
					{props.image}
				</div>
			</HoverVisible>
		</div>
	);
};

TreeBranch.defaultProps = {
	title: "",
	image: "",
	path: "",
	icon: "",
	selected: false,
	onClick: () => {},
	onImageClick: () => {},
	onTitleClick: () => {},
	onBranchClick: () => {},
};

export default TreeBranch;
