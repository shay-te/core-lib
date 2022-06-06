import React from 'react'
import { useDispatch } from "react-redux";
import { toggleSelected } from "../slices/treeSlice";
import CollapseExpand from "../collapseExpand/CollapseExpand";
import TreeBranch from "../treeBranch/TreeBranch";
import "./TreeSection.scss";

const TreeSection = (props) => {
	const dispatch = useDispatch();
	
	const onBranchClick = (path, event) => {
		dispatch(toggleSelected(path))
	}

	const items = [];
	if (props.isNested) {
		items.push(props.items);
	} else {
		for (const item of props.items) {
			items.push(
				<div key={item.name} className={"node-child"}>
					<TreeBranch
						onBranchClick={onBranchClick}
						path={item.path}
						onTitleClick={props.onClick}
						onImageClick={props.onDeleteClick}
						title={item.name}
						image={<i className="fa-solid fa-trash-can"></i>}
						key={item.name}
					/>
				</div>
			);
		}
	}
	return (
		<div className={["tree-section"]}>
			<div className={["node-title"]}>
				<TreeBranch
					onTitleClick={props.onTitleClick}
					onClick={props.onClick.bind(this, props.items)}
					path={props.path}
					onImageClick={props.onAddClick}
					title={props.title}
					image={<i className="fa-solid fa-plus"></i>}
					icon={props.icon}
					key={props.title}
				/>
			</div>
			<CollapseExpand key={props.title} collapsed={props.collapse}>{items}</CollapseExpand>
		</div>
	);
};

TreeSection.defaultProps = {
	title: "",
	path: "",
	items: [],
	icon: "",
	isNested: false,
	collapse: false,
	onClick: (item, e) => {},
	onDeleteClick: (item, e) => {},
	onAddClick: (item, e) => {},
	onTitleClick: (path) => {}
};

export default TreeSection;
