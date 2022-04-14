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
                            formFields={field}
                            index={index}
                            key={key}
                        />
                    );
                case "integer":
                    return (
                        <InputInteger
                            formFields={field}
                            index={index}
                            key={key}
                        />
                    );
                case "boolean":
                    return (
                        <InputBoolean
                            formFields={field}
                            index={index}
                            key={key}
                        />
                    );
                case "enum":
                    return (
                        <InputENUM
                            formFields={field}
                            index={index}
                            key={key}
                        />
                    );
                case "list":
                    return (
                        <InputList
                            formFields={field}
                            index={index}
                            key={key}
                        />
                    );
                case "dropdown":
                    return (
                        <InputDropDown
                            formFields={field}
                            index={index}
                            key={key}
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