import React, { useState } from "react";
import HoverVisible from "../hoverVisible/HoverVisible";
import TextField from "@mui/material/TextField";
import Checkbox from '@mui/material/Checkbox';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';

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
                            InputProps={{
                                style:{borderColor: '#d2e5fc', borderRadius: 15}
                            }}
                            defaultValue={column.key}
                            required={true}
                            label="Column Name"
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'key']),
                            })}
                            size='small'
                        />
                    </td>
                    <td key={props.keyObj.toString([props.fieldKey, index, 'type'])} className="td">
                        <FormControl size="small">
                            <InputLabel id="dropdown-select-helper-label">Column Type</InputLabel>
                            <Select
                                labelId="dropdown-select-helper-label"
                                label='Column Type'
                                style={{borderColor: '#d2e5fc', borderRadius: 15}}
                                id={props.keyObj.toString([props.fieldKey, index, 'type'])}
                                onChange={props.onChange.bind(this, {
                                    key: props.keyObj.toString([props.fieldKey, index, 'type']),
                                })}
                                value={column.type}
                            >
                                <MenuItem value="VARCHAR" size='small'>VARCHAR</MenuItem>
                                <MenuItem value="BOOLEAN" size='small'>BOOLEAN</MenuItem>
                                <MenuItem value="INTEGER" size='small'>INTEGER</MenuItem>
                            </Select>
                        </FormControl>
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'default'])}
                        className="td"
                    >
                        <TextField
                            type={"text"}
                            id={props.keyObj.toString(['field', props.fieldKey, index, 'default'])}
                            InputProps={{
                                style:{borderColor: '#d2e5fc', borderRadius: 15}
                            }}
                            defaultValue={column.default}
                            required={true}
                            label="Column Default Value"
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
