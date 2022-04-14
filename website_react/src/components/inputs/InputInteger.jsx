import { getDefault } from "../utils/commonUtils";

const InputInteger = (props) => {
    return (
        <div className="form-input-div" key={props.index}>
            <label htmlFor={"field-" + props.index} className="input-label">
                {props.title}
            </label>
            <input
                type={"number"}
                id={"field-" + props.index}
                className="form-input"
                defaultValue={getDefault(props)}
                required={props.mandatory}
                placeholder="Number input"
            />
        </div>
    );
};

export default InputInteger