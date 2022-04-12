import "./form.scss";
import InputString from "./../inputs/InputString";
import InputInteger from "./../inputs/InputInteger";
import InputBoolean from "./../inputs/InputBoolean";
import InputENUM from "./../inputs/InputENUM";
import InputList from "./../inputs/InputList";
import DBConnectionForm from "../dataCollectionForms/DBConnectionForm";
import DBEntityForm from "../dataCollectionForms/DBEntityForm";
const Form = (props) => {
	const formSubmit = (e) => {
		e.preventDefault();
		console.log(true);
	};

	return (
		<div>
			<form className="form-root" onSubmit={(e) => formSubmit(e)}>
				{props.fields.map((field, index) => {
					switch (field.type) {
						case "string":
							return (
								<InputString
									formFields={field}
									index={index}
									key={index}
								/>
							);
						case "integer":
							return (
								<InputInteger
									formFields={field}
									index={index}
									key={index}
								/>
							);
						case "boolean":
							return (
								<InputBoolean
									formFields={field}
									index={index}
									key={index}
								/>
							);
						case "enum":
							return (
								<InputENUM
									formFields={field}
									index={index}
									key={index}
								/>
							);
						case "list":
							return (
								<InputList
									formFields={field}
									index={index}
									key={index}
								/>
							);
					}
				})}
				<DBConnectionForm />
				<DBEntityForm />
				<input type={"submit"} className="submit-button" />
			</form>
		</div>
	);
};

export default Form;
