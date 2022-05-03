import { useState } from 'react';

import CollapseExpand from "../collapseExpand/CollapseExpand";
import "./TreeSection.scss";

const TreeSection = (props) => {
    const [collapse, setCollapse] = useState(false);
    const onItemClick = (item, event) => {}

    const items = [];
    for (const item of props.items) {
        items.push(<div key={item} onClick={onItemClick.bind(this, item)}>{item}</div>)
    }

	return (<div className={["tree-section"]}>
        <h3 onClick={() => {setCollapse(!collapse)}}>{props.title}</h3>
        <CollapseExpand collapsed={collapse}>
            {items}
        </CollapseExpand>
    </div>)
};


TreeSection.defaultProps = {
    title: '',
    items: [], 
    onItemClick: (item, e) => {}, //Fire the path
};

export default TreeSection;
