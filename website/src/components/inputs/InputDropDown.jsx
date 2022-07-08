import React from 'react'
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Tooltip from "@mui/material/Tooltip";

const InputDropDown = (props) => {
	const items =  props.options.map((value, index) => {
		return (
            <MenuItem id={props.keyObj.toString(['select', props.fieldKey])} key={index} value={value}>{value ? value : 'None'}</MenuItem>
		);
	});

	return (
	    <div className='form-input-div'>
            <Tooltip title={props.toolTipTitle} placement="right" arrow>
                <div>
                    <FormControl size="small">
                        <InputLabel id="dropdown-select-helper-label">{props.title}</InputLabel>
                        <Select
                            style={{borderColor: '#d2e5fc', borderRadius: 15}}
                            labelId="dropdown-select-helper-label"
                            id="dropdown-select-helper"
                            value={props.value}
                            label={props.title}
                            onChange={props.onChange}
                            className={props.fullWidth ? "form-input" : "form-input-small"}
                        >
                            {items}
                        </Select>
                    </FormControl>
                </div>
            </Tooltip>
        </div>
	);
};

InputDropDown.defaultProps = {
	fieldKey:'',
	title:'',
	mandatory:false,
	value:'',
	default_value:'',
	options:[],
	onChange: () => {},
    keyObj: Object,
    toolTipTitle: '',
    fullWidth: true,
}

export default InputDropDown;
