import "./form.scss";
import Fields from "./Fields";
const Form = () => {
	const formSubmit = (e) => {
		e.preventDefault();
		console.log(true);
	};
	
	return (
		<div>
			<form className="form-root" onSubmit={(e) => formSubmit(e)}>
				<Fields/>
			</form>
		</div>
	);
};

export default Form;
