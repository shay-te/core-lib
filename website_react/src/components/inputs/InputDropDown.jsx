import { getDefault } from "./../../utils/commonUtils";

const InputDropDown = (props) => {
	const items =  props.options.map((value, index) => {
		return (
			<option
				key={index}
				value={value}
				selected={value === getDefault(props)}
			>
				{value}
			</option>
		);
	});

	return (
		<div className="form-input-div">
			<label className="input-label">{props.title}</label>
			<br />
			<select name={props.title} id={props.fieldKey} onChange={props.onChange}>
				{items}
			</select>
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
}

export default InputDropDown;
