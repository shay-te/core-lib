import React, { useState, useEffect } from "react";
import HoverVisible from "../hoverVisible/HoverVisible";
import Checkbox from '@mui/material/Checkbox';
import InputString from "../inputs/InputString";
import { isBoolean, isNotNull, isNumber } from "../../utils/validatorUtils";
import InputDropDown from "../inputs/InputDropDown";

const ColumnsTable = (props) => {
    const [visible, setVisible] = useState(false);
    const [columns, setColumns] = useState([]);
    const items = [];
    useEffect(() => {
        if(columns.length !== props.value.length){
            setColumns(props.value)
        }
        
    }, [props.value.length])
    items.push(
        columns.map((column, index) => {
            let validatorCallback;
            if(column.type === 'INTEGER'){
                validatorCallback = isNumber
            } else if (column.type === 'BOOLEAN'){
                validatorCallback= isBoolean
            } else {
                validatorCallback = isNotNull
            }
            return (
                <tr
                    key={props.keyObj.toString([props.fieldKey, index, 'key', column.key])}
                    onMouseEnter={() => setVisible(true)}
                    onMouseLeave={() => setVisible(false)}
                    onMouseOver={() => setVisible(true)}
                    className="tr"
                >
                    <td key={props.keyObj.toString([props.fieldKey, index, 'key'])} className="td">
                        <InputString
                            key={props.keyObj.toString([props.fieldKey, index, 'key'])}
                            title={"Column Name"}
                            mandatory={column.nullable ? column.nullable : false}
                            value={column.key}
                            default_value={column.key}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'key']),
                            })}
                            fieldKey={props.fieldKey}
                            keyObj={props.keyObj}
                            fullWidth={false}
                            validatorCallback={isNotNull}
                        />
                    </td>
                    <td key={props.keyObj.toString([props.fieldKey, index, 'type'])} className="td">
                        <InputDropDown
                            key={props.keyObj.toString([props.fieldKey, index, 'type'])}
                            title={"Column Type"}
                            mandatory={true}
                            value={column.type}
                            default_value={column.type}
                            options={["VARCHAR", "BOOLEAN", "INTEGER"]}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'type']),
                            })}
                            fieldKey={props.fieldKey}
                            keyObj={props.keyObj}
                            fullWidth={false}
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'default'])}
                        className="td"
                    >
                        <InputString
                            key={props.keyObj.toString([props.fieldKey, index, 'default'])}
                            title={"Column Default Value"}
                            mandatory={column.nullable ? column.nullable : false}
                            value={column.default}
                            default_value={column.default}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'default']),
                            })}
                            fieldKey={props.fieldKey}
                            keyObj={props.keyObj}
                            fullWidth={false}
                            validatorCallback={validatorCallback}
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'nullable'])}
                        className="td"
                    >
                        <Checkbox 
                            id={props.keyObj.toString([props.fieldKey, index, 'nullable'])}
                            name={props.keyObj.toString(['checkbox', props.fieldKey, index, 'nullable'])}
                            value={column.nullable}
                            checked={column.nullable}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'nullable']),
                            })}
                            size='small'
                        />
                    </td>

                    <td className="td">
                        <HoverVisible isVisible={visible}>
                            <button
                                className="column-del-btn"
                                onClick={props.onDeleteClick.bind(
                                    this,
                                    `${props.fieldKey}.${index}`
                                )}
                            >
                                <i className="fa-solid fa-trash-can"></i>
                            </button>
                        </HoverVisible>
                    </td>
                </tr>
            );
        })
    );
    let render = '';
    if (columns.length !== 0) {
        render = 
            <table className="table">
                <thead>
                    <tr className="tr">
                        <th className="th">Name</th>
                        <th className="th">Type</th>
                        <th className="th">Default</th>
                        <th className="th">Nullable</th>
                    </tr>
                </thead>
                <tbody>{items}</tbody>
            </table>
    }
    return (
        <>
            <div className="table-info">Note: <code>id</code> column will be added automatically for every column</div>
            {render}
        </>
    );
};

ColumnsTable.defaultProps = {
    fieldKey: "",
    index: 1,
    onChange: () => {},
    onDeleteClick: () => {},
    title: "",
    value: [],
    keyObj: Object,
};

export default ColumnsTable;
