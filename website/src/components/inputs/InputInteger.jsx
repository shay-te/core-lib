import React, { useState} from 'react'
import TextField from '@mui/material/TextField';
import Tooltip from "@mui/material/Tooltip";

const InputInteger = (props) => {
    const [error, setError] = useState(false)

    const handleChange = (event) => {
        let validate = false
        validate = props.validatorCallback(event.target.value)
        if(!props.mandatory && event.target.value.length === 0){
            validate = true
        }
        setError(!validate)
        if(validate){
            props.onChange(event)
        }
        
    }

    const fieldId = props.keyObj.toString(["integer", props.fieldKey])
    return (
        <div className="form-input-div">  
            <Tooltip title={props.toolTipTitle} placement="right" arrow>
                <div>
                    <TextField
                        InputProps={{
                            className: "form-input",
                            style:{borderColor: '#d2e5fc', borderRadius: 15}
                        }}
                        type={"number"}
                        id={fieldId}
                        defaultValue={props.value || props.default_value}
                        required={props.mandatory}
                        placeholder={props.title}
                        onChange={handleChange.bind(this)}
                        label={props.title}
                        size="small"
                        error={error}
                        helperText={props.errorText}
                    />
                </div>
            </Tooltip>  
            
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
    validatorCallback: () => {},
    keyObj: Object,
    errorText: '',
    toolTipTitle: '',
}

export default InputInteger