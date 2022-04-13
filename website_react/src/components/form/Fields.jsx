import InputString from '../inputs/InputString'
import InputInteger from '../inputs/InputInteger'
import InputBoolean from '../inputs/InputBoolean'
import InputENUM from '../inputs/InputENUM'
import InputList from '../inputs/InputList'
import { useSelector } from "react-redux";

const Fields = (props) => {
    const fields = useSelector((state) => state.formData.fields)
    
    console.log(fields)
    return(
        
        <>
        {fields.map((field, index) => {
            switch (field.type.toLowerCase()) {
                case "string":
                case "varchar":
                    return (
                        <InputString
                            formFields={field}
                            index={index}
                            key={index+Math.floor((Math.random() * 1000) + 1)}
                        />
                    );
                case "integer":
                    return (
                        <InputInteger
                            formFields={field}
                            index={index}
                            key={index+Math.floor((Math.random() * 1000) + 1)}
                        />
                    );
                case "boolean":
                    return (
                        <InputBoolean
                            formFields={field}
                            index={index}
                            key={index+Math.floor((Math.random() * 1000) + 1)}
                        />
                    );
                case "enum":
                    return (
                        <InputENUM
                            formFields={field}
                            index={index}
                            key={index+Math.floor((Math.random() * 1000) + 1)}
                        />
                    );
                case "list":
                    return (
                        <InputList
                            formFields={field}
                            index={index}
                            key={index+Math.floor((Math.random() * 1000) + 1)}
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