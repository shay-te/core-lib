import React from "react";

import { useDispatch } from "react-redux";
import { deleteFormField, addNewEntry } from "../slices/treeSlice";

import "./InputTable.scss";
import FunctionsTable from "./FunctionsTable";
import ColumnsTable from "./ColumnsTable";

const InputTable = (props) => {
    const dispatch = useDispatch();

    const onDeleteClick = (path) => {
        dispatch(deleteFormField(path));
    };

    const onAddClick = (path) => {
        dispatch(addNewEntry(path));
    };
    let items = undefined

    if (props.type === "functions") {
        items = 
            <FunctionsTable
                index={props.index}
                key={props.fieldKey}
                title={props.title}
                value={props.value}
                onChange={props.onChange}
                fieldKey={props.fieldKey}
                onDeleteClick={onDeleteClick}
            />
        
    } else if (props.type === "columns") {
        items =
            <ColumnsTable
                index={props.index}
                key={props.fieldKey}
                title={props.title}
                value={props.value}
                onChange={props.onChange}
                fieldKey={props.fieldKey}
                onDeleteClick={onDeleteClick}
            />
    }

    return (
        <div className="columns-root">
            <div className="columns-title-div">
                <div className="columns-title">{props.title}</div>
                <button
                    className="column-add-btn"
                    onClick={() => onAddClick(`${props.fieldKey}`)}
                >
                    <i className="fa-solid fa-plus fa-xl"></i>
                </button>
            </div>

            <div>
                {items}
            </div>
        </div>
    );
};

InputTable.defaultProps = {
    fieldKey: "",
    index: 1,
    onChange: () => {},
    title: "",
    value: [],
    type: "",
};

export default InputTable;
