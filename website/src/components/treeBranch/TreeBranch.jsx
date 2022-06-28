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
			onClick={() => {props.onBranchClick(props.path)}}
			className={["tree-branch",treeSelected[props.path] ? "selected" : "",visible && props.showHover? "hover-branch" : ""].join(" ")}
		>
			<div
				className="branch-title-icon"
			>
				<div>{props.icon}</div>
				<div className="branch-title" onClick={() => {props.onTitleClick(props.path)}}>{props.title}</div>
			</div>
			<HoverVisible isVisible={visible}>
				<div
					onClick={props.onImageClick.bind(this, props.path)}
					className={[props.showHover? "hover-img" : ""].join(" ")}
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
    showHover: true,
	onClick: () => {},
	onImageClick: () => {},
	onTitleClick: () => {},
	onBranchClick: () => {},
};

export default TreeBranch;
