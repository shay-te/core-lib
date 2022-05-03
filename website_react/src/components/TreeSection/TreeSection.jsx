import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import CollapseExpand from "../collapseExpand/CollapseExpand";
import "./TreeSection.scss";

const TreeSection = (props) => {
	const [collapse, setCollapse] = useState(false);

	const items = [];
	for (const item of props.items) {
        if(item.hasOwnProperty('name') && item.hasOwnProperty('path')){
            items.push(
                <div
                    key={item.name}
                    onClick={props.onClick.bind(this, item)}
                    className={"node-child"}
                >
                    {item.name}
                </div>
            );
        } 
        else{            
            items.push(
                Object.keys(item).map(dbConn => {
                    return(
                        <div>
                            <div onClick={props.onClick.bind(this, dbConn)}> 
                                <span onClick={() => {setCollapse(!collapse)}}>{dbConn} </span>
                            </div>
                            <CollapseExpand collapsed={collapse}>
                                {
                                    item[dbConn].map(entity => {
                                        if(entity.name !== 'migrate'){
                                            return(
                                                <div
                                                    key={entity.name}
                                                    onClick={props.onClick.bind(this, entity)}
                                                    className={"node-child"}
                                                >
                                                    {entity.name}
                                                </div>
                                            )
                                        }
                                    })
                                }
                            </CollapseExpand>
                        </div>
                    )
                })
            )
        }       
	}

	return (
		<div className={["tree-section"]}>
			<div className={["node-title"]}>
				<div onClick={() => {setCollapse(!collapse)}}> {props.title} </div>
				<CollapseExpand collapsed={collapse}>{items}</CollapseExpand>
			</div>
		</div>
	);
};

TreeSection.defaultProps = {
	title: "",
	items: [],
	onClick: (item, e) => {}, //Fire the path
};

export default TreeSection;
