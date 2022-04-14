import InputString from '../inputs/InputString'
import InputInteger from '../inputs/InputInteger'
import InputBoolean from '../inputs/InputBoolean'
import InputENUM from '../inputs/InputENUM'
import InputList from '../inputs/InputList'
import { useSelector } from "react-redux";
import InputDropDown from '../inputs/InputDropDown'

const Fields = (props) => {
    const fields = useSelector((state) => state.formData.fields)

    return(
        <>
        {fields.map((field, index) => {
            const key = `${index}_${Math.floor((Math.random() * 100000) + 1)}`
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
                            target={field.target}
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
                        />
                    );
                case "dropdown":
                    return (
                        <InputDropDown
                            formFields={field}
                            index={index}
                            key={key}
                            title={field.title}
                            mandatory={field.mandatory}
                            value={field.value}
                            default_value={field.default_value}
                            options={field.options}
                        />
                    );
                default:
                    return ''
            }
        })}
        </>
    )
}

export default Fields