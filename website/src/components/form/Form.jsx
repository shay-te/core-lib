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
import { Key } from "../../utils/Key";

const Form = (props) => {
    const fields = useSelector((state) => state.treeData.fields);
    const title = useSelector((state) => state.treeData.fieldsTitle);
    const form = [];
    const key = new Key()
    form.push(
        fields.map((field, index) => {
            const fieldKey = field.key;
            switch (field.type.toLowerCase()) {
                case "string":
                case "varchar":
                    return (
                        <InputString
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            onChange={props.onChange.bind(this, field)}
                            fieldKey={fieldKey}
                            keyObj={key}
                        />
                    );
                case "integer":
                    return (
                        <InputInteger
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            onChange={props.onChange.bind(this, field)}
                            fieldKey={fieldKey}
                            keyObj={key}
                        />
                    );
                case "boolean":
                    return (
                        <InputBoolean
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            onChange={props.onChange.bind(this, field)}
                            fieldKey={fieldKey}
                            keyObj={key}
                        />
                    );
                case "enum":
                    return (
                        <InputENUM
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            multiple_selection={field.multiple_selection}
                            options={field.options}
                            onChange={props.onChange.bind(this, field)}
                            fieldKey={fieldKey}
                            keyObj={key}
                        />
                    );
                case "list":
                    return (
                        <InputList
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            multiple_selection={field.multiple_selection}
                            options={field.options}
                            onChange={props.onChange.bind(this, field)}
                            fieldKey={fieldKey}
                            keyObj={key}
                        />
                    );
                case "dropdown":
                    return (
                        <InputDropDown
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            options={field.options}
                            onChange={props.onChange.bind(this, field)}
                            fieldKey={fieldKey}
                            keyObj={key}
                        />
                    );
                case "columns":
                case "functions":
                    return (
                        <InputTable
                            type={field.type.toLowerCase()}
                            index={index}
                            key={fieldKey}
                            title={field.title}
                            value={field.value}
                            onChange={props.onChange}
                            fieldKey={fieldKey}
                            keyObj={key}
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
