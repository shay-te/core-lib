import React from 'react'
import TextField from '@mui/material/TextField';

const InputString = (props) => {
    const getDefault = () => {
        if(props.value===undefined) return props.default_value
        else return props.value
    }
    const fieldId = props.keyObj.toString(["field", props.fieldKey])
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <TextField 
                InputProps={{
                    className: "form-input",
                }}
                type={"text"}
                id={fieldId}
                defaultValue={getDefault()}
                required={props.mandatory}
                placeholder={props.title}
                onChange={props.onChange}
                label={props.title}
                size="small"
            />
        </div>
    );
};

InputString.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:'',
    value:'',
    default_value:'',
    onChange: () => {},
    keyObj: Object,
}

export default InputString