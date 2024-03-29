import React from 'react'
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import FormLabel from '@mui/material/FormLabel';
import Tooltip from "@mui/material/Tooltip";

const InputENUM = (props) => {

    const items = props.options.map((value, index) => {
        const fieldId = props.keyObj.toString(["enum", props.fieldKey])
        return (
            <FormControlLabel
                control={props.multiple_selection
                    ? <Checkbox 
                        checked={
                            value.toLowerCase() === (props.value.toLowerCase() || props.default_value.toLowerCase())
                        }
                        size="small"
                    />
                    : <Radio 
                        checked={
                            value.toLowerCase() === (props.value.toLowerCase() || props.default_value.toLowerCase())
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
    });

    return (
        <div className="form-input-div">
            <Tooltip title={props.toolTipTitle} placement="right" arrow>
                <div>
                    <FormLabel id="radio-buttons-group-enum">{props.title}</FormLabel>
                    <RadioGroup
                        aria-labelledby="radio-buttons-group-enum"
                        name={props.fieldKey}
                    >
                        {items}
                    </RadioGroup>
                </div>
            </Tooltip>
            
        </div>
    );
};

InputENUM.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory: true,
    value:'',
    default_value:'',
    multiple_selection:false,
    options:[],
    keyObj: Object,
    toolTipTitle: '',
}

export default InputENUM