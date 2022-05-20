import React from 'react'
import CollapseExpand from "../collapseExpand/CollapseExpand";
import TreeBranch from "../treeBranch/TreeBranch";
import "./TreeSection.scss";
import Delete from '@site/assets/delete.png';
import Add from '@site/assets/add.png';

const TreeSection = (props) => {
	const items = [];
	if (props.isNested) {
		items.push(props.items);
	} else {
		for (const item of props.items) {
			items.push(
				<div key={item.name} className={"node-child"}>
					<TreeBranch
						path={item.path}
						onTitleClick={props.onClick}
						onImageClick={props.onDeleteClick}
						title={item.name}
						image={Delete}
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
					image={Add}
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
