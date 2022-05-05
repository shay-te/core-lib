import { useDispatch, useSelector } from "react-redux";
import "./tree.scss";
import TreeSection from "../TreeSection/TreeSection";
import { setFields } from "../slices/treeSlice";

const Tree = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const entities = useSelector((state) => state.treeData.entities);
	const dispatch = useDispatch()

	const onDataAccessClick = (item, event) => {
		console.log('item.path', item.path)
		dispatch(setFields(item.path))
	}
	const onCoreLibClick = (item) => {
		dispatch(setFields(item.path))
	}
	const onSetupClick = (item) => {
		dispatch(setFields('setup'))
	}
	const onEntityClick = (item, event) => {
		dispatch(setFields(item.path))
	}
	const onItemClick = (item, event) => {
		dispatch(setFields(item.path))
    };


	const dbConnectionElements = []
	dbConnections.forEach(dbConn => {
		entities.forEach(connectionEntity => {
			if(connectionEntity.hasOwnProperty(dbConn.name)){
				dbConnectionElements.push(
					<TreeSection key={dbConn.name} title={dbConn.name} items={connectionEntity[dbConn.name]} onClick={onEntityClick}/>
				)
			}
		})
	})
	
	const RenderTree = () => {
		return (
			<div className="tree-root">
				<div className="tree">
					<div className={["node-title"]} onClick={() => onCoreLibClick()}>{CoreLibName}</div>
					<TreeSection key={'data_access'} title="Data Access" items={dataAccess} onClick={onDataAccessClick} isNested={false}/>
					<TreeSection key={'db'} title="DB Entities" items={dbConnectionElements} onClick={onItemClick} isNested={true}/>
					<div className={["node-title"]} onClick={() => onSetupClick()}>Setup</div>
				</div>
			</div>
		);
	};

	return <RenderTree />;
};

export default Tree;
