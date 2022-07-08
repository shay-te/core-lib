import React, { useEffect, useState } from "react";
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
import FormTitleSubtitle from "../FormTitleSubtitle/FormTitleSubtitle";
import FormButton from "../FormButton/FormButton";
import FieldsFactory from "../../utils/FieldsFactory";

const Form = (props) => {
    const [fields, setFields] = useState([])
    const  fieldsFactory = new FieldsFactory()
    const selectedField = useSelector((state) => state.treeData.selectedField);
    const yaml = useSelector((state) => state.treeData.yaml);
    useEffect(() => {
        setFields(fieldsFactory.generate(selectedField, yaml))
    }, [selectedField, yaml])
    const form = [];
    const key = new Key()
    if(fields.length > 0) {
        form.push(
            fields.map((field, index) => {
                const handleChange = (event) => {
                    props.onChange(field, event)
                }
                const fieldKey = field.key;
                const toolTipTitle = field.toolTipTitle ? field.toolTipTitle : ''
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
                                onChange={handleChange}
                                fieldKey={fieldKey}
                                keyObj={key}
                                helperText={field.helperText}
                                validatorCallback={field.validatorCallback}
                                toolTipTitle={toolTipTitle}
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
                                onChange={handleChange}
                                fieldKey={fieldKey}
                                keyObj={key}
                                validatorCallback={field.validatorCallback}
                                toolTipTitle={toolTipTitle}
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
                                toolTipTitle={field.toolTipTitle ? field.toolTipTitle : {yes: '', no: ''}}
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
                                toolTipTitle={toolTipTitle}
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
                                toolTipTitle={toolTipTitle}
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
                    case "title_subtitle":
                        return(
                            <FormTitleSubtitle
                                index={index}
                                key={fieldKey}
                                title={field.title}
                                subtitle={field.subtitle}
                                fieldKey={fieldKey}
                                keyObj={key}
                            />
                        )
                    case "button":
                        return(
                            <FormButton
                                index={index}
                                key={fieldKey}
                                label={field.label}
                                onClick={field.onClick}
                                fieldKey={fieldKey}
                                keyObj={key}
                            />
                        )
                    default:
                        return "";
                }
            })
        );
    }

    return (
        <div className="form-root custom-scrollbar">
            {form}
        </div>
    );
};

export default Form;
