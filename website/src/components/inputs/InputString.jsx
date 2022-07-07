import React, { useState} from 'react'
import TextField from '@mui/material/TextField';
import FormHelperText from '@mui/material/FormHelperText';
import Tooltip from "@mui/material/Tooltip";

const InputString = (props) => {
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

    const getDefault = () => {
        if(props.value===undefined) return props.default_value
        else return props.value
    }

    const fieldId = props.keyObj.toString(["field", props.fieldKey])
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <Tooltip title={props.toolTipTitle} placement="right" arrow>
                <div>
                    <TextField 
                        InputProps={{
                            className: props.fullWidth ? "form-input" : "form-input-small",
                            style:{borderColor: '#d2e5fc', borderRadius: 15},
                        }}
                        type={"text"}
                        id={fieldId}
                        defaultValue={getDefault()}
                        required={props.mandatory}
                        placeholder={props.title}
                        onChange={handleChange.bind(this)}
                        label={props.title}
                        size="small"
                        error={error}
                    />
                    <FormHelperText id="component-helper-text">
                        {props.helperText}
                    </FormHelperText>
                </div>
            </Tooltip>
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
    validatorCallback: () => {},
    helperText: '',
    keyObj: Object,
    toolTipTitle: '',
    fullWidth: true,
}

export default InputString