import React, { useState, useEffect } from "react";
import HoverVisible from "../hoverVisible/HoverVisible";
import { Checkbox} from "@mui/material";
import { isNotNull, isSnakeCaseCapital } from "../../utils/validatorUtils";
import InputString from "../inputs/InputString";

const FunctionsTable = (props) => {
    const [functions, setFunctions] = useState([]);
    const [visible, setVisible] = useState(false);
    const items = [];
    const isDataAccess = props.fieldKey.includes('core_lib.data_accesses.');
    useEffect(() => {
        if(functions.length !== props.value.length){
            setFunctions(props.value)
        }
        
    }, [props.value.length])
    items.push(
        functions.map((func, index) => {
            return (
                <tr
                    key={props.keyObj.toString([props.fieldKey, index, 'key', func.key])}
                    onMouseEnter={() => setVisible(true)}
                    onMouseLeave={() => setVisible(false)}
                    onMouseOver={() => setVisible(true)}
                    className="tr"
                >
                    <td key={props.keyObj.toString([props.fieldKey, index, 'key'])} className="td">
                        <InputString
                            index={index}
                            key={props.keyObj.toString([props.fieldKey, index, 'key'])}
                            title={"Function Name"}
                            mandatory={true}
                            value={func.key}
                            default_value={func.key}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'key']),
                            })}
                            fieldKey={props.fieldKey}
                            keyObj={props.keyObj}
                            validatorCallback={isNotNull}
                            fullWidth={false}
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
                        <InputString
                            index={index}
                            key={props.keyObj.toString([props.fieldKey, index, 'cache_key'])}
                            title={"Cache key"}
                            mandatory={false}
                            value={func.cache_key ? func.cache_key : ''}
                            default_value={func.cache_key ? func.cache_key : ''}
                            onChange={props.onChange.bind(this, {
                                key: props.keyObj.toString([props.fieldKey, index, 'cache_key']),
                            })}
                            fieldKey={props.fieldKey}
                            keyObj={props.keyObj}
                            validatorCallback={isSnakeCaseCapital}
                            toolTipTitle={'Cache key in CAPITAL LETTERS'}
                            fullWidth={false}
                        />
                    </td>
                    <td
                        key={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate'])}
                        className={isDataAccess ? "hide" : "td"}
                    >
                        <Checkbox
                            key={props.keyObj.toString([props.fieldKey, index, 'cache_invalidate', func.cache_invalidate])}
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
    if (functions.length !== 0) {
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
