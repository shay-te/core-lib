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
import Tooltip from "@mui/material/Tooltip";
import FormTitleSubtitle from "../FormTitleSubtitle/FormTitleSubtitle";
import FormButton from "../FormButton/FormButton";

const Form = (props) => {
    const fields = useSelector((state) => state.treeData.fields);
    const title = useSelector((state) => state.treeData.fieldsTitle);
    const form = [];
    const key = new Key()
    form.push(
        fields.map((field, index) => {
            const fieldKey = field.key;
            const toolTipTitle = field.toolTipTitle ? field.toolTipTitle : ''
            switch (field.type.toLowerCase()) {
                case "string":
                case "varchar":
                    return (
                        <Tooltip title={String(toolTipTitle)} placement='right' arrow>
                            <div>
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
                                    helperText={field.helperText}
                                />
                            </div>
                        </Tooltip>
                    );
                case "integer":
                    return (
                        <Tooltip title={String(toolTipTitle)} placement='right' arrow>
                            <div>
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
                            </div>
                        </Tooltip>
                    );
                case "boolean":
                    return (
                        <Tooltip title={String(toolTipTitle)} placement='right' arrow>
                            <div>
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
                            </div>
                        </Tooltip>
                    );
                case "enum":
                    return (
                        <Tooltip title={String(toolTipTitle)} placement='right' arrow>
                            <div>
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
                            </div>
                        </Tooltip>
                    );
                case "list":
                    return (
                        <Tooltip title={String(toolTipTitle)} placement='right' arrow>
                            <div>
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
                            </div>
                        </Tooltip>
                    );
                case "dropdown":
                    return (
                        <Tooltip title={String(toolTipTitle)} placement='right' arrow>
                            <div>
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
                            </div>
                        </Tooltip>
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

    return (
        <div className="form-root custom-scrollbar">
            {form}
        </div>
    );
};

export default Form;
