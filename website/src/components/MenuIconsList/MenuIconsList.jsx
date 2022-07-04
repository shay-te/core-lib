import React from 'react';
import './MenuIconsList.scss'
import Tooltip from '@mui/material/Tooltip';

const MenuIconsList = (props) => {
    const renderTopIcons = []
    const renderBottomIcons = []   

    const renderIcon = (tooltipTitle, item, onClick, selected) => {
        return(
            <Tooltip title={tooltipTitle} placement='right' arrow>
                <div onClick={() => onClick()} className={`list-icon ${selected? 'selected' : ''}`}>
                    {item}
                </div>
            </Tooltip> 
        )
    }
    props.topMenuItems.forEach((item) => {
        renderTopIcons.push(
            renderIcon(item.tooltipTitle, item.item, item.onClick(), item.selected)
        )
    })

    props.bottomMenuItems.forEach((item) => {
        renderBottomIcons.push(
            renderIcon(item.tooltipTitle, item.item, item.onClick(), item.selected)
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