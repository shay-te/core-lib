import React from 'react';
import MenuIconsList from "../MenuIconsList/MenuIconsList"
import './MenuIcons.scss'

import { useDispatch, useSelector } from "react-redux";
import {
    setList,
    setFields
} from "../slices/treeSlice";

const MenuIcons = () => {
    const selected = useSelector((state) => state.treeData.selectedConfig);
    const yaml = useSelector((state) => state.treeData.yaml);
    const dispatch = useDispatch();

    const onDataAccessClick = () => {
        dispatch(setList('data_accesses'));
        if(yaml.core_lib.data_accesses.length > 0){
            dispatch(setFields({ title: "Data Access", path: "core_lib.data_accesses.0"}));
        }
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
        if(yaml.core_lib.entities.length > 0){
            dispatch(setFields({ title: "Data Access", path: "core_lib.entities.0"}));
        }
    };
    const onConnectionClick = () => {
        dispatch(setList('connections'));
        if(yaml.core_lib.connections.length > 0){
            dispatch(setFields({ title: "Data Access", path: "core_lib.connections.0"}));
        }
    };
    const onCacheClick = () => {
        dispatch(setList('caches'));
        if(yaml.core_lib.caches.length > 0){
            dispatch(setFields({ title: "Data Access", path: "core_lib.caches.0"}));
        }
    };
    const onServiceClick = () => {
        dispatch(setList('services'));
        if(yaml.core_lib.services.length > 0){
            dispatch(setFields({ title: "Data Access", path: "core_lib.services.0"}));
        }
    }
    const onJobClick = () => {
        dispatch(setList('jobs'));
        if(yaml.core_lib.jobs.length > 0){
            dispatch(setFields({ title: "Data Access", path: "core_lib.jobs.0"}));
        }
    };
    const onExportClick = () => {
        dispatch(setList('export'));
    };
    let showEntity = false
    const entityIcon = {
        tooltipTitle: 'Edit Entities',
        item: <i className={`icon fa-solid fa-database`}></i>,
        selected: selected === 'entities',
        onClick: onEntityClick,
    };
    if(JSON.stringify(yaml) !== '{}'){
        yaml.core_lib.connections.forEach((connection) => {
            if (connection.type.includes("SqlAlchemyConnectionRegistry")) {
                showEntity = true
            }
        });
    }

    const topMenuItems = [
        {
            tooltipTitle: 'Edit Core-Lib',
            item: <img className={`core-lib-image icon`} src={require('../../assets/img/core-lib-black.png')}/>,
            selected: selected === 'core_lib',
            onClick: onCoreLibClick,
        },
        {
            tooltipTitle: 'Edit Connections',
            item: <i className={`icon fa-solid fa-circle-nodes`}></i>,
            selected: selected === 'connections',
            onClick: onConnectionClick,
        },
        {
            tooltipTitle: 'Edit Caches',
            item: <i className={`icon fa-solid fa-server`}></i>,
            selected: selected === 'caches',
            onClick: onCacheClick,
        },
        {
            tooltipTitle: 'Edit Services',
            item: <i className={`icon fa-solid fa-network-wired`}></i>,
            selected: selected === 'services',
            onClick: onServiceClick,
        },
        {
            tooltipTitle: 'Edit Data Accesses',
            item: <i className={`icon fa-solid fa-list`}></i>,
            selected: selected === 'data_accesses',
            onClick: onDataAccessClick,
        },
        {
            tooltipTitle: 'Edit Jobs',
            item: <i className={`icon fa-solid fa-spinner`}></i>,
            selected: selected === 'jobs',
            onClick: onJobClick,
        },
        {
            tooltipTitle: 'Edit Setup',
            item: <i className={`icon fa-solid fa-gear`}></i>,
            selected: selected === 'setup',
            onClick: onSetupClick,
        },

    ]

    const bottomMenuItems = [
        {
            tooltipTitle: 'Export Core-Lib',
            item: <i className={`icon fa-solid fa-file-export`}></i>,
            selected: selected === 'export',
            onClick: onExportClick,
        },
    ]

    if(showEntity && topMenuItems.length === 7){
        topMenuItems.splice(4, 0, entityIcon)
    } else {
        if(topMenuItems.length === 8){
            topMenuItems.splice(4, 1)
        }
    }

    return(
        <MenuIconsList topMenuItems={topMenuItems} bottomMenuItems={bottomMenuItems}/>
    )
}

export default MenuIcons