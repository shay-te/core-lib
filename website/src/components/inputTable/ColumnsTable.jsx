import React, { useState } from "react";
import HoverVisible from "../hoverVisible/HoverVisible";
import TextField from "@mui/material/TextField";
import { Checkbox, MenuItem, Select } from "@mui/material";

const ColumnsTable = (props) => {
    const [visible, setVisible] = useState(false);

    const items = [];
    items.push(
        props.value.map((column, index) => {
            return (
                <tr
                    key={index}
                    onMouseEnter={() => setVisible(true)}
                    onMouseLeave={() => setVisible(false)}
                    onMouseOver={() => setVisible(true)}
                    className="tr"
                >
                    <td key={props.keyObj.toString([props.fieldKey, index, 'key'])} className="td">
                        <TextField
                            type={"text"}
                            id={props.keyObj.toString(['field', props.fieldKey, index, 'key'])}
                            className="form-input"
                            defaultValue={column.key}
                            required={true}
                            placeholder="Column Name"
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'key']),
                            })}
                            size='small'
                        />
                    </td>
                    <td key={props.keyObj.toString([props.fieldKey, index, 'type'])} className="td">
                        <Select
                            id={props.keyObj.toString([props.fieldKey, index, 'type'])}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'type']),
                            })}
                            value={column.type}
                            size='small'
                        >
                            <MenuItem value="VARCHAR" size='small'>VARCHAR</MenuItem>
                            <MenuItem value="BOOLEAN" size='small'>BOOLEAN</MenuItem>
                            <MenuItem value="INTEGER" size='small'>INTEGER</MenuItem>
                        </Select>
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'default'])}
                        className="td"
                    >
                        <TextField
                            type={"text"}
                            id={props.keyObj.toString(['field', props.fieldKey, index, 'default'])}
                            className="form-input"
                            defaultValue={column.default}
                            required={true}
                            placeholder="Column Default Value"
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'default']),
                            })}
                            size='small'
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
    if (props.value.length !== 0) {
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
    return <>{render}</>;
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
