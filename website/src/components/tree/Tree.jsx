import React from "react";
import { useDispatch, useSelector } from "react-redux";
import "./tree.scss";
import TreeSection from "../TreeSection/TreeSection";
import {
    setFields,
    deleteTreeBranch,
    addNewEntry,
    toggleCollapseExpand,
    init
} from "../slices/treeSlice";
import { download } from "../../utils/commonUtils";
import YAML from "yaml";
import { useEffect } from "react";
import { useHistory } from '@docusaurus/router';

const Tree = () => {
    const dataAccess = useSelector((state) => state.treeData.dataAccess);
    const connections = useSelector((state) => state.treeData.connections);
    const entities = useSelector((state) => state.treeData.entities);
    const jobs = useSelector((state) => state.treeData.jobs);
    const cache = useSelector((state) => state.treeData.cache);
    const services = useSelector((state) => state.treeData.services);
    const yaml = useSelector((state) => state.treeData.yaml);
    const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
    const treeState = useSelector((state) => state.treeData.treeState);
    const dispatch = useDispatch();
    const history = useHistory();
    useEffect(() => {
        if(JSON.stringify(yaml) === '{}'){
            const recentCoreLib = JSON.parse(localStorage.getItem('recent_core_lib'))
            if(recentCoreLib){
                dispatch(init(recentCoreLib))
            } else {
                history.push('/generate')
            }
        }
    }, [])
    

    const onDataAccessClick = (path) => {
        dispatch(setFields({ title: "Data Access", path: path }));
    };
    const onCoreLibClick = (item) => {
        dispatch(setFields({ title: "Core-Lib", path: "name" }));
    };
    const onSetupClick = (item) => {
        dispatch(setFields({ title: "Data Access", path: "setup" }));
    };
    const onEntityClick = (path) => {
        dispatch(setFields({ title: "Entity", path: path }));
    };
    const onConnectionClick = (path) => {
        dispatch(setFields({ title: "Connection", path: path }));
    };
    const onCacheClick = (path) => {
        dispatch(setFields({ title: "Cache", path: path }));
    };
    const onServiceClick = (path) => {
        dispatch(setFields({ title: "Service", path: path }));
    }
    const onJobClick = (path) => {
        dispatch(setFields({ title: "Job", path: path }));
    };
    const onDeleteClick = (path) => {
        dispatch(deleteTreeBranch(path));
    };
    const onAddEntity = (path) => {
        dispatch(addNewEntry("db_entities"));
    };
    const onAddDataAccess = (path) => {
        dispatch(addNewEntry("data_accesses"));
    };
    const onAddConnection = (path) => {
        dispatch(addNewEntry("connections"));
    };
    const onAddCache = (path) => {
        dispatch(addNewEntry("caches"));
    };
    const onAddJob = (path) => {
        dispatch(addNewEntry("jobs"));
    };

    const onAddService = (path) => {
        dispatch(addNewEntry("services"));
    }

    const onCollapseExpand = (path) => {
        dispatch(toggleCollapseExpand(path));
    };
    const exportYaml = () => {
        const doc = new YAML.Document();
        doc.contents = yaml;
        download(doc.toString(), `${CoreLibName}.yaml`);
    };
    let entitySection = "";
    if(JSON.stringify(yaml) !== '{}'){
        yaml.core_lib.connections.forEach((connection) => {
            if (connection.type.includes("SqlAlchemyConnectionRegistry")) {
                entitySection = (
                    <TreeSection
                        key={"db_entities"}
                        path={"db_entities"}
                        title="DB Entities"
                        items={entities}
                        onDeleteClick={onDeleteClick}
                        onAddClick={onAddEntity}
                        onTitleClick={onCollapseExpand}
                        onClick={onEntityClick}
                        collapse={treeState["db_entities"]}
                        icon={<i className="fa-solid fa-database fa-sm"></i>}
                    />
                );
                return
            }
        });
    }

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
                        key={"data_accesses"}
                        path={"data_accesses"}
                        title="Data Access"
                        items={dataAccess}
                        onClick={onDataAccessClick}
                        onDeleteClick={onDeleteClick}
                        isNested={false}
                        onAddClick={onAddDataAccess}
                        onTitleClick={onCollapseExpand}
                        collapse={treeState["data_accesses"]}
                        icon={<i className="fa-solid fa-list fa-sm"></i>}
                    />
                    <TreeSection
                        key={"connections"}
                        path={"connections"}
                        title="Connections"
                        items={connections}
                        onDeleteClick={onDeleteClick}
                        onClick={onConnectionClick}
                        isNested={false}
                        onAddClick={onAddConnection}
                        onTitleClick={onCollapseExpand}
                        collapse={treeState["connections"]}
                        icon={
                            <i className="fa-solid fa-circle-nodes fa-sm"></i>
                        }
                    />
                    {entitySection}
                    <TreeSection
                        key={"services"}
                        path={"services"}
                        title="Services"
                        items={services}
                        onDeleteClick={onDeleteClick}
                        onClick={onServiceClick}
                        isNested={false}
                        onAddClick={onAddService}
                        onTitleClick={onCollapseExpand}
                        collapse={treeState["services"]}
                        icon={<i className="fa-solid fa-network-wired fa-sm"></i>}
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
                        icon={<i className="fa-solid fa-spinner fa-sm"></i>}
                    />
                    <TreeSection
                        key={"caches"}
                        path={"caches"}
                        title="Cache"
                        items={cache}
                        onDeleteClick={onDeleteClick}
                        collapse={treeState["caches"]}
                        onClick={onCacheClick}
                        isNested={false}
                        onAddClick={onAddCache}
                        onTitleClick={onCollapseExpand}
                        icon={<i className="fa-solid fa-server fa-sm"></i>}
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
