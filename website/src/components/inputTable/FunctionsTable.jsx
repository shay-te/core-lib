import React, { useState } from "react";
import HoverVisible from "../hoverVisible/HoverVisible";
import { Checkbox, TextField } from "@mui/material";

const FunctionsTable = (props) => {
    const [visible, setVisible] = useState(false);
    const items = [];
    const isDataAccess = props.fieldKey.includes('core_lib.data_accesses.');
    items.push(
        
        props.value.map((func, index) => {
            
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
                            defaultValue={func.key}
                            required={true}
                            label="Function Name"
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'key']),
                            })}
                            size='small'
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'result_to_dict'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <Checkbox
                            key={props.keyObj.toString([props.fieldKey, index, 'result_to_dict'])}
                            id={props.keyObj.toString([props.fieldKey, index, 'result_to_dict'])}
                            name={props.keyObj.toString(['checkbox', props.fieldKey, index, 'result_to_dict'])}
                            value={func.result_to_dict}
                            checked={func.result_to_dict}
                            disabled={isDataAccess}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'result_to_dict']),
                            })}
                            size='small'
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'cache_key'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <TextField
                            key={props.keyObj.toString([props.fieldKey, index, 'cache_key'])}
                            type={"text"}
                            id={props.keyObj.toString(['field', props.fieldKey, index, 'cache_key'])}
                            InputProps={{
                                style:{borderColor: '#d2e5fc', borderRadius: 15}
                            }}
                            value={func.cache_key ? func.cache_key : ''}
                            required={true}
                            placeholder="Cache key"
                            label="Cache key"
                            disabled={isDataAccess}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'cache_key']),
                            })}
                            size='small'
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <Checkbox
                            key={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate'])}
                            id={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate'])}
                            name={props.keyObj.toString(['checkbox', props.fieldKey, index, 'cache_invalidate'])}
                            value={func.cache_invalidate}
                            checked={func.cache_invalidate}
                            disabled={isDataAccess}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'cache_invalidate']),
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
                        <th className={isDataAccess ? "hide" : "th"}>Result To Dict</th>
                        <th className={isDataAccess ? "hide" : "th"}>Cache Key</th>
                        <th className={isDataAccess ? "hide" : "th"}>Cache Invalidate</th>
                    </tr>
                </thead>
                <tbody>{items}</tbody>
            </table>
    }
    return <>{render}</>;
};

FunctionsTable.defaultProps = {
    fieldKey: "",
    index: 1,
    onChange: () => {},
    onDeleteClick: () => {},
    title: "",
    value: [],
    keyObj: Object,
};

export default FunctionsTable;
