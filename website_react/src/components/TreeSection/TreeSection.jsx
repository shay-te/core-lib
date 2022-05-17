import { useState } from "react";

import CollapseExpand from "../collapseExpand/CollapseExpand";
import TreeBranch from "../treeBranch/TreeBranch";
import "./TreeSection.scss";

const TreeSection = (props) => {
	const [collapse, setCollapse] = useState(false);

	const handleCollapse = () => {
		setCollapse(!collapse);
	};

	const items = [];
	if (props.isNested) {
		items.push(props.items);
	} else {
		for (const [i, item] of props.items.entries()) {
			items.push(
				<div key={item.name} className={"node-child"}>
					<TreeBranch
						path={item.path}
						onTitleClick={props.onClick}
						onImageClick={props.onDeleteClick}
						title={item.name}
						image={require("../../assets/delete.png")}
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
					image={require("../../assets/add.png")}
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
