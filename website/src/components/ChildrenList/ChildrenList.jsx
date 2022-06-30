import React from "react"
import TitleChildren from "../TitleChildren/TitleChildren"
import { useDispatch, useSelector } from "react-redux";
import {
    setFields,
    addNewEntry,
    deleteTreeBranch
} from "../slices/treeSlice";

import './ChildrenList.scss'

const ChildrenList = () => {
    const dataAccess = useSelector((state) => state.treeData.dataAccess);
    const connections = useSelector((state) => state.treeData.connections);
    const entities = useSelector((state) => state.treeData.entities);
    const jobs = useSelector((state) => state.treeData.jobs);
    const cache = useSelector((state) => state.treeData.cache);
    const services = useSelector((state) => state.treeData.services);
    const selected = useSelector((state) => state.treeData.selectedConfig);
    const dispatch = useDispatch();

    const onDataAccessClick = (path) => {
        dispatch(setFields({ title: "Data Access", path: path }));
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
    const onExportClick = (path) => {
        dispatch(setFields({ path }));
    };
    const onDeleteClick = (path, event) => {
        event.stopPropagation();
        dispatch(deleteTreeBranch(path));
    };
    const onAddEntity = (connection) => {
        dispatch(addNewEntry(`db_entities.${connection}`));
    };
    const onAddDataAccess = () => {
        dispatch(addNewEntry("data_accesses"));
    };
    const onAddConnection = () => {
        dispatch(addNewEntry("connections"));
    };
    const onAddCache = () => {
        dispatch(addNewEntry("caches"));
    };
    const onAddJob = () => {
        dispatch(addNewEntry("jobs"));
    };

    const onAddService = () => {
        dispatch(addNewEntry("services"));
    }

    const items = []
    switch (selected) {
        case "core_lib":
            items.push(
                <TitleChildren 
                    key={'core_lib'}
                    title='Core-Lib' 
                    showAdd={false}
                />
            )
            break;
        case "data_accesses":
            items.push(
                <TitleChildren 
                    key={'data_accesses'}
                    title='Data Accesses' 
                    children={dataAccess} 
                    onClick={onDataAccessClick}
                    onAddClick={onAddDataAccess}
                    onDeleteClick={onDeleteClick}
                />
            )
            break;
        case "connections":
            items.push(
                <TitleChildren 
                    key={'connections'}
                    title='Connections' 
                    children={connections} 
                    onClick={onConnectionClick}
                    onAddClick={onAddConnection}
                    onDeleteClick={onDeleteClick}
                />
            )
            break;
        case "entities":
            entities.forEach(entity => {
                items.push(
                    <TitleChildren 
                        key={entity.connection}
                        title={entity.connection}
                        children={entity.entities} 
                        onClick={onEntityClick}
                        onAddClick={onAddEntity}
                        onDeleteClick={onDeleteClick}
                    />
                )
            });
            
            break;
        case "services":
            items.push(
                <TitleChildren 
                    key={'services'}
                    title='Services' 
                    children={services} 
                    onClick={onServiceClick}
                    onAddClick={onAddService}
                    onDeleteClick={onDeleteClick}
                />
            )
            break;
        case "jobs":
            items.push(
                <TitleChildren 
                    key={'jobs'}
                    title='Jobs' 
                    children={jobs} 
                    onClick={onJobClick}
                    onAddClick={onAddJob}
                    onDeleteClick={onDeleteClick}
                />
            )
            break;
        case "caches":
            items.push(
                <TitleChildren 
                    key={'caches'}
                    title='Caches' 
                    children={cache} 
                    onClick={onCacheClick}
                    onAddClick={onAddCache}
                    onDeleteClick={onDeleteClick}
                />
            )
            break;
        case "setup":
            items.push(
                <TitleChildren 
                    key={'setup'}
                    title='Setup' 
                    showAdd={false}
                />
            )
            break;
        case "export":
            items.push(
                <TitleChildren 
                    key={'export'}
                    title='Export'
                    children={[{name: 'Export YAML', path: 'export_yaml'}, {name: 'Download ZIP', path: 'download_zip'}]}
                    showAdd={false}
                    showDelete={false}
                    onClick={onExportClick}
                />
            )
            break;
    }
    return(
        <div className="children-list-root custom-scrollbar">
            {items}
        </div>
    )
}

export default ChildrenList