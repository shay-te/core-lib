import React from 'react';
import MenuChildrenList from '../MenuChildrenList/MenuChildrenList';
import MenuIcons from '../MenuIcons/MenuIcons';
import './DoubleMenu.scss'

const DoubleMenu = () => {
    return(
        <div className="double-menu-root">
            <MenuIcons/>
            <MenuChildrenList/>
        </div>
    )
}

export default DoubleMenu