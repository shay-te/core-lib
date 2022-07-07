import React from 'react';
import './MenuIconsList.scss'
import Tooltip from '@mui/material/Tooltip';

const MenuIconsList = (props) => {
    const renderTopIcons = []
    const renderBottomIcons = []   
    
    props.topMenuItems.forEach((item) => {
        renderTopIcons.push(
            <Tooltip title={item.tooltipTitle} placement='right' arrow>
                <div onClick={() => item.onClick()} className={`list-icon ${item.selected? 'selected' : ''}`}>
                    {item.item}
                </div>
            </Tooltip> 
        )
        
    })

    props.bottomMenuItems.forEach((item) => {
        renderBottomIcons.push(
            <Tooltip title={item.tooltipTitle} placement='right' arrow>
                <div onClick={() => item.onClick()} className={`list-icon ${item.selected? 'selected' : ''}`}>
                    {item.item}
                </div>
            </Tooltip> 
        )
        
    })


    return(
        <div className="icons-list-root custom-scrollbar">
            <div className="top-icons-list">
                {renderTopIcons}
            </div>
            <div className="bottom-icons-list">
                {renderBottomIcons}
            </div>
        </div>
    )
}

MenuIconsList.defaultProps = {
    topMenuItems: [],
    bottomMenuItems: [],
};

export default MenuIconsList