import { useDispatch, useSelector } from "react-redux";
import "./tree.scss";
import TreeSection from "../TreeSection/TreeSection";
import { dataAccessFields } from "../fieldsGenerator/dataAccessFields";
import { setFields } from "../slices/formSlice";
import { entityFields } from "../fieldsGenerator/entityFields";
import { coreLibField } from "../fieldsGenerator/coreLibField";
import { setupFields } from "../fieldsGenerator/setupFields";
import { dbConnectionFields } from "../fieldsGenerator/dbConnectionFields";

const Tree = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const setup = useSelector((state) => state.treeData.setup);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const entities = useSelector((state) => state.treeData.entities);
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch()

	const onDataAccessClicked = (item, event) => {
		dispatch(setFields(dataAccessFields(item.name, CoreLibName, dbConnections, yamlData)))
	}
	const onItemClick = (item, event) => {
		if(item instanceof Object){
			if(item.path.includes('data_access')){
				
			}
			else if(item.path.includes('data_layers.data')){
				dispatch(setFields(entityFields(item.dbConnection, item.name, CoreLibName, dbConnections, yamlData)))
			}
			else if(item.path.includes('core_lib')){
				dispatch(setFields(coreLibField(item.name)))
			}
			else if(item.path.includes('setup')){
				dispatch(setFields(setupFields(item.name, yamlData)))
			}
		}
        
		else{
			dispatch(setFields(dbConnectionFields(item, CoreLibName, yamlData)))
		}
    };

	const entitiesComp = [];
	for (const entity of Object.keys(entities)) {
		entitiesComp.push(<TreeSection title={entity.name} items={dataAccess} onClick={onItemClick}/>)
	}

	// extract the connection name from the config 
	// const connectionAEntities = [
	// 
	//]
	// <TreeSection title='connection_a' items={connectionAEntities}></TreeSection>

	// items.push(
	// 	Object.keys(item).map(dbConn => {
	// 		return(
	// 			<div>
	// 				<div onClick={props.onClick.bind(this, dbConn)}> 
	// 					<span onClick={() => {setCollapse(!collapse)}}>{dbConn} </span>
	// 				</div>
	// 				<CollapseExpand collapsed={collapse}>
	// 					{
	// 						item[dbConn].map(entity => {
	// 							if(entity.name !== 'migrate'){
	// 								return(
	// 									<div
	// 										key={entity.name}
	// 										onClick={props.onClick.bind(this, entity)}
	// 										className={"node-child"}
	// 									>
	// 										{entity.name}
	// 									</div>
	// 								)
	// 							}
	// 						})
	// 					}
	// 				</CollapseExpand>
	// 			</div>
	// 		)
	// 	})
	// )
	
	const RenderTree = () => {
		return (
			<div className="tree-root">
				<div className="tree">
					<div className={["node-title"]} onClick={(e) => onItemClick({name: CoreLibName, path: 'core_lib'}, e)}>{CoreLibName}</div>
					<TreeSection title="Data Access" items={dataAccess} onClick={onItemClick}/>
					<TreeSection title="DB Entities" items={entities} onClick={onItemClick}/>
					
					<div className={["node-title"]} onClick={(e) => onItemClick({name: CoreLibName, path: 'setup'}, e)}>Setup</div>
				</div>
			</div>
		);
	};

	return <RenderTree />;
};

export default Tree;
