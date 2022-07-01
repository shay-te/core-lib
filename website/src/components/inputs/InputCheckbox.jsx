import { Checkbox } from '@mui/material';
import React from 'react'

const InputCheckbox = (props) => {
    const fieldId = props.keyObj.toString(["checkbox", props.fieldKey])
    return (
        <div className="form-input-div">
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
        </div>
    );
};

InputCheckbox.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    onChange: () => {},
    keyObj: Object,
}

export default InputCheckbox