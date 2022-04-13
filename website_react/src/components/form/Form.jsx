import "./form.scss";
import Fields from "./Fields";
const Form = (props) => {
	const formSubmit = (e) => {
		e.preventDefault();
		console.log(true);
	};
	
	return (
		<div>
			<form className="form-root" onSubmit={(e) => formSubmit(e)}>
				<Fields fields={props.fields} />
				<input type={"submit"} className="submit-button" />
			</form>
		</div>
	);
};

export default Form;
