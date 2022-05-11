import "./form.scss";
import InputString from '../inputs/InputString'
import InputInteger from '../inputs/InputInteger'
import InputBoolean from '../inputs/InputBoolean'
import InputENUM from '../inputs/InputENUM'
import InputList from '../inputs/InputList'
import { useSelector } from "react-redux";
import InputDropDown from '../inputs/InputDropDown'

const Form = (props) => {
    const fields = useSelector((state) => state.treeData.fields)
    const form = []
    form.push(
        fields.map((field, index) => {
            const key = `${field.id ? field.id : index}`
            switch (field.type.toLowerCase()) {
                case "string":
                case "varchar":
                    return (
                        <InputString
                            key={key}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            onChange={props.onChange.bind(this, field)}
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
                        />
                    );
                default:
                    return ''
            }
        })
    )

    return(
        <div className="form-root">
            {form}
        </div>
    )
}

export default Form