import React from "react"
import MenuTitleChildren from "../MenuTitleChildren/MenuTitleChildren"
import { useDispatch, useSelector } from "react-redux";
import {
    setFields,
    addNewEntry,
    deleteTreeBranch
} from "../slices/treeSlice";

import './MenuChildrenList.scss'
import Pathsfactory from "../../utils/PathsFactory";

const MenuChildrenList = () => {
    const yaml = useSelector((state) => state.treeData.yaml);
    const pathsFactory = new Pathsfactory()
    const dataAccess = pathsFactory.listPaths('core_lib.data_accesses', yaml);
    const connections = pathsFactory.listPaths('core_lib.connections', yaml);
    const entities = pathsFactory.listPaths('core_lib.entities', yaml);
    const jobs = pathsFactory.listPaths('core_lib.jobs', yaml);
    const cache = pathsFactory.listPaths('core_lib.caches', yaml);
    const services = pathsFactory.listPaths('core_lib.services', yaml);
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


    const renderMenuTitle = (key, title, noEntriesMessage = '', children = [], showAdd = false, showDelete = false, showChildren = false,  onClick = () => {}, onAddClick = () => {}) => {
       return <MenuTitleChildren 
            key={key}
            title={title} 
            items={children}
            showAdd={showAdd}
            showDelete={showDelete}
            showChildren={showChildren}
            onClick={onClick}
            onAddClick={onAddClick}
            onDeleteClick={onDeleteClick}
            noEntriesMessage={noEntriesMessage}
        />
    }

    const items = []
    switch (selected) {
        case "core_lib":
            items.push(
                renderMenuTitle('core_lib', 'Core-Lib')
            )
            break;
        case "data_accesses":
            items.push(
                renderMenuTitle('data_accesses', 'Data Accesses', 'No Data Accesses added yet.', dataAccess, true, true , true, onDataAccessClick, onAddDataAccess)
            )
            break;
        case "connections":
            items.push(
                renderMenuTitle('connections', 'Connections', 'No Connections added yet.', connections, true, true , true, onConnectionClick, onAddConnection)
            )
            break;
        case "entities":
            entities.forEach(entity => {
                items.push(
                    renderMenuTitle(entity.connection, entity.connection, 'No Entities added to this connection yet.', entity.entities, true, true , true, onEntityClick, onAddEntity)
                )
            });
            
            break;
        case "services":
            items.push(
                renderMenuTitle('services', 'Services', 'No Services added yet.', services, true, true , true, onServiceClick, onAddService)
            )
            break;
        case "jobs":
            items.push(
                renderMenuTitle('jobs', 'Jobs', 'No Jobs added yet.', jobs, true, true , true, onJobClick, onAddJob)
            )
            break;
        case "caches":
            items.push(
                renderMenuTitle('caches', 'Caches', 'No Caches added yet.', cache, true, true , true, onCacheClick, onAddCache)
            )
            break;
        case "setup":
            items.push(
                renderMenuTitle('setup', 'Setup')
            )
            break;
        case "export":
            const exportChildren = [{name: 'Export YAML', path: 'export_yaml'}, {name: 'Download ZIP', path: 'download_zip'}]
            items.push(
                renderMenuTitle('export', 'Export', '', exportChildren, false, false, true, onExportClick)
            )
            break;
    }
    return(
        <div className="children-list-root custom-scrollbar">
            {items}
        </div>
    )
}

export default MenuChildrenList