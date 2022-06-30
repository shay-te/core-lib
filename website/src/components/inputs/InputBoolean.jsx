import React from 'react'
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import ToolTip from '@mui/material/ToolTip';


const InputBoolean = (props) => {
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <FormLabel id="bool-radio-grp">{props.title}</FormLabel>
            <RadioGroup
                aria-labelledby="bool-radio-grp"
                name="bool-radio-grp"
            >
                <FormControlLabel 
                    value={true} 
                    key={props.keyObj.toString(["true", props.fieldKey])}
                    control={
                        <Radio 
                            id={props.keyObj.toString(["true", props.fieldKey])}
                            name={props.keyObj.toString(["bool", props.fieldKey])}
                            value={true}
                            checked={props.value || props.default_value}
                            required={props.mandatory}
                            onChange={props.onChange}
                            size='small'
                        />
                    } 
                    label="Yes" 
                />
                <FormControlLabel 
                    value={true} 
                    key={props.keyObj.toString(["false", props.fieldKey])}
                    control={
                        <Radio 
                            id={props.keyObj.toString(["false", props.fieldKey])}
                            name={props.keyObj.toString(["bool", props.fieldKey])}
                            value={false}
                            checked={!(props.value || props.default_value)}
                            required={props.mandatory}
                            onChange={props.onChange}
                            size='small'
                        />
                    } 
                    label="No" 
                />
            </RadioGroup>
        </div>
    );
};

InputBoolean.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:false,
    default_value:false,
    onChange: () => {},
}

export default InputBoolean