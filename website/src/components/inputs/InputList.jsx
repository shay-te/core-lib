import React from 'react'
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Tooltip from "@mui/material/Tooltip";

const InputList = (props) => {

    const fieldId = props.keyObj.toString(["list", props.fieldKey])
    const items = props.options.map((value, index) => {
        return (
            <FormControlLabel
                control={props.multiple_selection
                    ? <Checkbox 
                        checked={
                            props.value.includes(value) || props.default_value.includes(value)
                        }
                        size="small"
                    />
                    : <Radio 
                        checked={
                            props.value.includes(value) || props.default_value.includes(value)
                        }
                        size="small"
                    />}
                id={fieldId}
                name={fieldId}
                value={value}
                onChange={props.onChange}
                label={value}
            />
        );
    })

    return (
        <div className="form-input-div">
            <Tooltip title={props.toolTipTitle} placement="right" arrow>
                <div>
                    <label className="input-label">{props.title}</label>
                    <RadioGroup
                        aria-labelledby="radio-buttons-group-list"
                        name={props.fieldKey}
                    >
                        {items}
                    </RadioGroup>
                </div>
            </Tooltip>
            
        </div>
    );
};

InputList.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    options: [],
    multiple_selection: false,
    onChange: () => {},
    keyObj: Object,
    toolTipTitle: '',
}

export default InputList