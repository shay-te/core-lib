import React from 'react'
import TextField from '@mui/material/TextField';

const InputInteger = (props) => {
    const fieldId = props.keyObj.toString(["integer", props.fieldKey])
    return (
        <div className="form-input-div">    
            <TextField
                InputProps={{
                    className: "form-input",
                }}
                type={"number"}
                id={fieldId}
                defaultValue={props.value || props.default_value}
                required={props.mandatory}
                placeholder={props.title}
                onChange={props.onChange}
                label={props.title}
                size="small"
            />
        </div>
    );
};

InputInteger.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    onChange: () => {},
    keyObj: Object,
}

export default InputInteger