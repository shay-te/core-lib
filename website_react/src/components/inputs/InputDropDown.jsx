import { getDefault } from "../utils/commonUtils";

const InputDropDown = (props) => {
	const RenderItems = () => {
		return props.formFields.options.map((value, index) => {
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
	};

	return (
		<div className="form-input-div" key={props.index}>
			<label className="input-label">{props.formFields.title}</label>
			<br />
			<select name={props.formFields.title} id={props.index}>
				<RenderItems />
			</select>
		</div>
	);
};

export default InputDropDown;
