const InputDropDown = (props) => {
	
	const items =  props.options.map((value, index) => {
		return (
			<option
				key={index}
				value={value}
			>
				{value}
			</option>
		);
	});

	return (
		<div className="form-input-div">
			<label className="input-label">{props.title}</label>
			<br />
			<select name={props.title} id={props.fieldKey} onChange={props.onChange} value ={props.value || props.default_value}>
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
