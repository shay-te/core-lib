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

	const onItemClick = (item, event) => {
		if(item instanceof Object){
			if(item.path.includes('data_access')){
				dispatch(setFields(dataAccessFields(item.name, CoreLibName, dbConnections, yamlData)))
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
