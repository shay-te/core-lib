import React, {useState} from "react"
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import HoverVisible from "../hoverVisible/HoverVisible";
import './MenuTitleChildren.scss';

const HandleChildRenderEvents = (props) => {
    const [isVisible, setIsVisible] = useState(false)
    const selectedField = useSelector((state) => state.treeData.selectedField);
    
    return(
            <div 
                onMouseEnter={() => setIsVisible(true)}
                onMouseLeave={() => setIsVisible(false)}
                onMouseOver={() => setIsVisible(true)}
                key={props.index} 
                className={`child ${selectedField === props.path ? 'selected' : ''}`} 
                onClick={() => props.onClick(props.path)}
            >
                <div className="child-name">
                    {props.name}
                </div>
                {
                    props.showDelete ?
                        <HoverVisible isVisible={isVisible}>
                            <div className="delete-img" onClick={props.onDeleteClick.bind(this, props.path)}>
                                <i className="fa-solid fa-trash-can fa-sm"></i>
                            </div>
                        </HoverVisible>
                    : ''
                }
                
            </div>
        
    )
}

const MenuTitleChildren = (props) => {
    const children = []
    useEffect(()=>{}, [props.items])
    props.items.forEach((child, index) => {
        children.push(
           <HandleChildRenderEvents key={index} path={child.path} name={child.name} index={index} onClick={props.onClick} onDeleteClick={props.onDeleteClick} showDelete={props.showDelete}/>
        )
    })

    let renderChildren = ''
    if(props.showChildren){
        renderChildren = (children.length > 0 ? children : <div className={`child child-info`}>{props.noEntriesMessage}</div>)
    }
    
    return(
        <div className="title-children-root">
            <div className="title-div">
                <div className="title">
                    {props.title} 
                </div>
                <div className="add-img">
                    {props.showAdd ? <i onClick={() => props.onAddClick(props.title)} className="fa-solid fa-plus fa-sm"></i> : ''}
                </div>
            </div>
            <div className="children">
                {renderChildren}
            </div>
        </div>
    )
}

MenuTitleChildren.defaultProps = {
    title:'',
    items: [],
    onClick: () => {},
    onAddClick: () => {},
    onDeleteClick: () => {},
    showAdd: true,
    showDelete: true,
    showChildren: true,
    noEntriesMessage: '',
}

export default MenuTitleChildren