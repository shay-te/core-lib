import React from "react";

import HoverVisible from "../hoverVisible/HoverVisible";
import { useState } from "react";

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
                        <input
                            type={"text"}
                            id={props.keyObj.toString(['field', props.fieldKey, index, 'key'])}
                            className="form-input"
                            defaultValue={func.key}
                            required={true}
                            placeholder="Name"
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'key']),
                            })}
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'result_to_dict'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <input
                            key={props.keyObj.toString([props.fieldKey, index, 'result_to_dict'])}
                            type="checkbox"
                            id={props.keyObj.toString([props.fieldKey, index, 'result_to_dict'])}
                            name={props.keyObj.toString(['checkbox', props.fieldKey, index, 'result_to_dict'])}
                            value={func.result_to_dict}
                            defaultChecked={func.result_to_dict}
                            disabled={isDataAccess}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'result_to_dict']),
                            })}
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'cache_key'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <input
                            key={props.keyObj.toString([props.fieldKey, index, 'cache_key'])}
                            type={"text"}
                            id={props.keyObj.toString(['field', props.fieldKey, index, 'cache_key'])}
                            className="form-input"
                            value={func.cache_key ? func.cache_key : ''}
                            required={true}
                            placeholder="Cache key"
                            disabled={isDataAccess}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'cache_key']),
                            })}
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <input
                            type="checkbox"
                            id={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate'])}
                            name={props.keyObj.toString(['checkbox', props.fieldKey, index, 'cache_invalidate'])}
                            value={func.cache_invalidate}
                            defaultChecked={func.cache_invalidate}
                            disabled={isDataAccess}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'cache_invalidate']),
                            })}
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
