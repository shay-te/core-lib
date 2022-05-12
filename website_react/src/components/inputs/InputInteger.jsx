import { getDefault } from "./../../utils/commonUtils";

const InputInteger = (props) => {
    return (
        <div className="form-input-div">
            <label htmlFor={"field-" + props.fieldKey} className="input-label">
                {props.title}
            </label>
            <input
                type={"number"}
                id={"field-" + props.fieldKey}
                className="form-input"
                defaultValue={getDefault(props)}
                required={props.mandatory}
                placeholder="Number input"
                onChange={props.onChange}
            />
        </div>
    );
};

InputInteger.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    onChange: () => {},
}

export default InputInteger