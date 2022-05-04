import { useDispatch, useSelector } from "react-redux";
import "./tree.scss";
import TreeSection from "../TreeSection/TreeSection";
import { dataAccessFields } from "./../../fieldsGenerator/dataAccessFields";
import { setFields } from "../slices/formSlice";
import { entityFields } from "./../../fieldsGenerator/entityFields";
import { coreLibField } from "./../../fieldsGenerator/coreLibField";
import { setupFields } from "./../../fieldsGenerator/setupFields";
import { dbConnectionFields } from "./../../fieldsGenerator/dbConnectionFields";
import { useEffect } from "react";
import { testInput } from './../../testInput';
import {
	init
} from "../../components/slices/treeSlice";

const Tree = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const entities = useSelector((state) => state.treeData.entities);
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch()

	const onDataAccessClick = (item, event) => {
		dispatch(setFields(dataAccessFields(item.path, yamlData)))
	}
	const onCoreLibClick = () => {
		dispatch(setFields(coreLibField(yamlData)))
	}
	const onSetupClick = () => {
		dispatch(setFields(setupFields(yamlData)))
	}
	const onEntityClick = (item, event) => {
		dispatch(setFields(entityFields(item.path, yamlData)))
	}
	const onItemClick = (item, event) => {
		dispatch(setFields(dbConnectionFields(item, CoreLibName, yamlData)))
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
