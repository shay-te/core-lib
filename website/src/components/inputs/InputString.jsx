import React from 'react'
import TextField from '@mui/material/TextField';
import FormHelperText from '@mui/material/FormHelperText';

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
                    style:{borderColor: '#d2e5fc', borderRadius: 15},
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
            <FormHelperText id="component-helper-text">
                {props.helperText}
            </FormHelperText>
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
    helperText: '',
    keyObj: Object,
}

export default InputString