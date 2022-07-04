import React, { useState } from 'react';
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
            item: <img className={`core-lib-image icon`} src={require('@site/static/img/core-lib-black.png').default}/>,
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
            arr.splice(4, 1)
        }
    }

    return(
        <MenuIconsList topMenuItems={topMenuItems} bottomMenuItems={bottomMenuItems}/>
    )
}

export default MenuIcons