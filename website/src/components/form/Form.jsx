import React from "react";
import "./form.scss";
import InputString from "../inputs/InputString";
import InputInteger from "../inputs/InputInteger";
import InputBoolean from "../inputs/InputBoolean";
import InputENUM from "../inputs/InputENUM";
import InputList from "../inputs/InputList";
import { useSelector } from "react-redux";
import InputDropDown from "../inputs/InputDropDown";
import InputTable from "../inputTable/InputTable";

const Form = (props) => {
	const fields = useSelector((state) => state.treeData.fields);
	const title = useSelector((state) => state.treeData.fieldsTitle);
	const form = [];
	form.push(
		fields.map((field, index) => {
			const key = `${field.key}`;
			switch (field.type.toLowerCase()) {
				case "string":
				case "varchar":
					return (
						<InputString
							index={index}
							key={key}
							title={field.title}
							mandatory={field.mandatory}
							value={field.value}
							default_value={field.default_value}
							onChange={props.onChange.bind(this, field)}
							fieldKey={key}
						/>
					);
				case "integer":
					return (
						<InputInteger
							index={index}
							key={key}
							title={field.title}
							mandatory={field.mandatory}
							value={field.value}
							default_value={field.default_value}
							onChange={props.onChange.bind(this, field)}
							fieldKey={key}
						/>
					);
				case "boolean":
					return (
						<InputBoolean
							index={index}
							key={key}
							title={field.title}
							mandatory={field.mandatory}
							value={field.value}
							default_value={field.default_value}
							onChange={props.onChange.bind(this, field)}
							fieldKey={key}
						/>
					);
				case "enum":
					return (
						<InputENUM
							index={index}
							key={key}
							title={field.title}
							mandatory={field.mandatory}
							value={field.value}
							default_value={field.default_value}
							multiple_selection={field.multiple_selection}
							options={field.options}
							onChange={props.onChange.bind(this, field)}
							fieldKey={key}
						/>
					);
				case "list":
					return (
						<InputList
							index={index}
							key={key}
							title={field.title}
							mandatory={field.mandatory}
							value={field.value}
							default_value={field.default_value}
							multiple_selection={field.multiple_selection}
							options={field.options}
							onChange={props.onChange.bind(this, field)}
							fieldKey={key}
						/>
					);
				case "dropdown":
					return (
						<InputDropDown
							index={index}
							key={key}
							title={field.title}
							mandatory={field.mandatory}
							value={field.value}
							default_value={field.default_value}
							options={field.options}
							onChange={props.onChange.bind(this, field)}
							fieldKey={key}
						/>
					);
				case "columns":
				case "functions":
					return (
						<InputTable
							type={field.type.toLowerCase()}
							index={index}
							key={key}
							title={field.title}
							value={field.value}
							onChange={props.onChange}
							fieldKey={key}
						/>
					);
				default:
					return "";
			}
		})
	);

	return (
		<div className="form-root">
			<h2>{title}</h2>
			{form}
		</div>
	);
};

export default Form;
