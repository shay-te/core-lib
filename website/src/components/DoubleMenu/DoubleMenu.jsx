import React, { useEffect } from 'react';
import MenuChildrenList from '../MenuChildrenList/MenuChildrenList';
import MenuIconsList from "../MenuIconsList/MenuIconsList"
import './DoubleMenu.scss'

import { useSelector, useDispatch } from "react-redux";
import {
    init,
} from "../slices/treeSlice";
import { useHistory } from '@docusaurus/router';

const DoubleMenu = () => {
    const yaml = useSelector((state) => state.treeData.yaml);
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

    return(
        <div className="double-menu-root">
            <MenuIconsList/>
            <MenuChildrenList/>
        </div>
    )
}

export default DoubleMenu