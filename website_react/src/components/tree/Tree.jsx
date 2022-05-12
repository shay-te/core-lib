import { useDispatch, useSelector } from "react-redux";
import "./tree.scss";
import TreeSection from "../TreeSection/TreeSection";
import {
	setFields,
	deleteTreeBranch,
	addNewEntry,
	toggleCollapseExpand,
} from "../slices/treeSlice";
import { download } from "../../utils/commonUtils";
import YAML from "yaml";

const Tree = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const entities = useSelector((state) => state.treeData.entities);
	const jobs = useSelector((state) => state.treeData.jobs);
	const cache = useSelector((state) => state.treeData.cache);
	const yaml = useSelector((state) => state.treeData.yaml);
	const treeState = useSelector((state) => state.treeData.treeState);
	const dispatch = useDispatch();

	const onDataAccessClick = (path) => {
		dispatch(setFields(path));
	};
	const onCoreLibClick = (item) => {
		dispatch(setFields("CoreLibName"));
	};
	const onSetupClick = (item) => {
		dispatch(setFields("setup"));
	};
	const onEntityClick = (path) => {
		dispatch(setFields(path));
	};
	const onDbConnClick = (path) => {
		dispatch(setFields(path));
	};

	const onCacheClick = (path) => {
		dispatch(setFields(path));
	};
	const onJobClick = (path) => {
		dispatch(setFields(path));
	};
	const onDeleteClick = (path) => {
		dispatch(deleteTreeBranch(path));
	};
	const onAddEntity = (path) => {
		dispatch(addNewEntry(path));
	};
	const onAddDataAccess = (path) => {
		dispatch(addNewEntry("data_access"));
	};
	const onAddDBConnection = (path) => {
		dispatch(addNewEntry("db_connection"));
	};
	const onAddCache = (path) => {
		dispatch(addNewEntry("config.cache"));
	};
	const onAddJob = (path) => {
		dispatch(addNewEntry("config.jobs"));
	};

	const onCollapseExpand = (path) => {
		dispatch(toggleCollapseExpand(path));
	};

	// const json2yaml = require('./../../utils/json2yaml').json2yaml;
	const exportYaml = () => {
		const doc = new YAML.Document();
		doc.contents = yaml;
		download(doc.toString(), `${CoreLibName}.yaml`);
	};

	const dbConnectionElements = [];
	dbConnections.forEach((dbConn) => {
		let entityList = [];
		entities.forEach((connectionEntity) => {
			if (connectionEntity.hasOwnProperty(dbConn.name)) {
				entityList = connectionEntity[dbConn.name];
			}
		});
		dbConnectionElements.push(
			<TreeSection
				path={`db_entity.${dbConn.name}`}
				key={dbConn.name}
				title={dbConn.name}
				items={entityList}
				onClick={onEntityClick}
				onDeleteClick={onDeleteClick}
				onAddClick={onAddEntity}
				onTitleClick={onCollapseExpand}
				collapse={treeState[`db_entity.${dbConn.name}`]}
			/>
		);
	});

	const RenderTree = () => {
		return (
			<div className="tree-root">
				<div className="tree">
					<div
						className={["node-title"]}
						onClick={() => onCoreLibClick()}
					>
						{CoreLibName}
					</div>
					<TreeSection
						key={"data_access"}
						path={"data_access"}
						title="Data Access"
						items={dataAccess}
						onClick={onDataAccessClick}
						onDeleteClick={onDeleteClick}
						isNested={false}
						onAddClick={onAddDataAccess}
						onTitleClick={onCollapseExpand}
						collapse={treeState["data_access"]}
						icon={<i class="fa-solid fa-list fa-sm"></i>}
					/>
					<TreeSection
						key={"db_entities"}
						path={"db_entities"}
						title="DB Entities"
						items={dbConnectionElements}
						onDeleteClick={onDeleteClick}
						onTitleClick={onCollapseExpand}
						isNested={true}
						collapse={treeState["db_entities"]}
						icon={<i class="fa-solid fa-database fa-sm"></i>}
					/>
					<TreeSection
						key={"db_connections"}
						path={"db_connections"}
						title="DB Connections"
						items={dbConnections}
						onDeleteClick={onDeleteClick}
						onClick={onDbConnClick}
						isNested={false}
						onAddClick={onAddDBConnection}
						onTitleClick={onCollapseExpand}
						collapse={treeState["db_connections"]}
						icon={<i class="fa-solid fa-circle-nodes fa-sm"></i>}
					/>
					<TreeSection
						key={"jobs"}
						path={"jobs"}
						title="Jobs"
						items={jobs}
						onDeleteClick={onDeleteClick}
						onClick={onJobClick}
						isNested={false}
						onAddClick={onAddJob}
						onTitleClick={onCollapseExpand}
						collapse={treeState["jobs"]}
						icon={<i class="fa-solid fa-spinner fa-sm"></i>}
					/>
					<TreeSection
						key={"cache"}
						path={"cache"}
						title="Cache"
						items={cache}
						onDeleteClick={onDeleteClick}
						collapse={treeState["cache"]}
						onClick={onCacheClick}
						isNested={false}
						onAddClick={onAddCache}
						onTitleClick={onCollapseExpand}
						icon={<i class="fa-solid fa-server fa-sm"></i>}
					/>
					<div
						className={["node-title"]}
						onClick={() => onSetupClick()}
					>
						Setup
					</div>
					<button
						className="export-button"
						onClick={() => exportYaml()}
					>
						Export
					</button>
				</div>
			</div>
		);
	};

	return <RenderTree />;
};

export default Tree;
