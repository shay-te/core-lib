import { useSelector } from "react-redux";
import "./tree.scss";
import CollapseExpand from "../collapseExpand/CollapseExpand";
import { useEffect, useState } from "react";

const Tree = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const setup = useSelector((state) => state.treeData.setup);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const entities = useSelector((state) => state.treeData.entities);

	const [hideDA, setHideDA] = useState(false);

	const RenderTree = () => {
		return (
			<div className="tree-root">
				<div className="tree">
					{dataAccess !== {} ? (
						<div className="node-title">
							<div onClick={() => setHideDA(!hideDA)}>
								Data Access
							</div>
							<CollapseExpand
								data={dataAccess}
								hide={hideDA}
							/>
						</div>
					) : (
						""
					)}
				</div>
			</div>
		);
	};

	return <RenderTree />;
};

export default Tree;
