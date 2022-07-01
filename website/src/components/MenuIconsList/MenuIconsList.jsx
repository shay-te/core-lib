import React, { useEffect } from 'react';
import './MenuIconsList.scss'

import { useDispatch, useSelector } from "react-redux";
import {
    setList,
    setFields
} from "../slices/treeSlice";
import Tooltip from '@mui/material/Tooltip';

const MenuIconsList = () => {
    const selected = useSelector((state) => state.treeData.selectedConfig);
    const yaml = useSelector((state) => state.treeData.yaml);
    const dispatch = useDispatch();

    const onDataAccessClick = () => {
        dispatch(setList('data_accesses'));
    };
    const onCoreLibClick = () => {
        dispatch(setList('core_lib'));
        dispatch(setFields({ title: "Core-Lib", path: "name" }));
    };
    const onSetupClick = () => {
        dispatch(setList('setup'));
        dispatch(setFields({ title: "Setup", path: "setup" }));
    };
    const onEntityClick = () => {
        dispatch(setList('entities'));
    };
    const onConnectionClick = () => {
        dispatch(setList('connections'));
    };
    const onCacheClick = () => {
        dispatch(setList('caches'));
    };
    const onServiceClick = () => {
        dispatch(setList('services'));
    }
    const onJobClick = () => {
        dispatch(setList('jobs'));
    };
    const onExportClick = () => {
        dispatch(setList('export'));
    };

    let entityIcon = "";
    if(JSON.stringify(yaml) !== '{}'){
        yaml.core_lib.connections.forEach((connection) => {
            if (connection.type.includes("SqlAlchemyConnectionRegistry")) {
                entityIcon = (
                    <Tooltip title="Edit Entities" placement='right' arrow>
                        <i onClick={() => onEntityClick()} className={`list-icon ${selected === 'entities' ? 'selected' : ''} fa-solid fa-database`}></i>
                    </Tooltip>
                );
            }
        });
    }

    return(
        <div className="icons-list-root custom-scrollbar">
            <div className="icons-list">
                <Tooltip title="Edit Core-Lib Name" placement='right' arrow>
                    <img onClick={() => onCoreLibClick()} className={`core-lib-image list-icon ${selected === 'core_lib' ? 'selected' : ''}`} src={require('@site/static/img/core-lib-black.png').default}/>
                </Tooltip>
                <Tooltip title="Edit Connections" placement='right' arrow>
                    <i onClick={() => onConnectionClick()} className={`list-icon ${selected === 'connections' ? 'selected' : ''} fa-solid fa-circle-nodes`}></i>    
                </Tooltip>
                <Tooltip title="Edit Caches" placement='right' arrow>
                    <i onClick={() => onCacheClick()} className={`list-icon ${selected === 'caches' ? 'selected' : ''} fa-solid fa-server`}></i>
                </Tooltip>
                <Tooltip title="Edit Services" placement='right' arrow>
                    <i onClick={() => onServiceClick()}  className={`list-icon ${selected === 'services' ? 'selected' : ''} fa-solid fa-network-wired`}></i>
                </Tooltip>
                <Tooltip title="Edit Data Accesses" placement='right' arrow>
                    <i onClick={() => onDataAccessClick()} className={`list-icon ${selected === 'data_accesses' ? 'selected' : ''} fa-solid fa-list`}></i>
                </Tooltip>
                {entityIcon}
                <Tooltip title="Edit Jobs" placement='right' arrow>
                    <i onClick={() => onJobClick()} className={`list-icon ${selected === 'jobs' ? 'selected' : ''} fa-solid fa-spinner`}></i>
                </Tooltip>
                
                <Tooltip title="Edit Setup" placement='right' arrow>
                    <i onClick={() => onSetupClick()} className={`list-icon ${selected === 'setup' ? 'selected' : ''} fa-solid fa-gear`}></i>
                </Tooltip>
            </div>
            <div className="export-icon">
                <Tooltip title="Export Core-Lib" placement='right' arrow>
                    <i onClick={() => onExportClick()} className={`list-icon ${selected === 'export' ? 'selected' : ''} fa-solid fa-file-export`}></i>
                </Tooltip>
            </div>
        </div>
    )
}

export default MenuIconsList