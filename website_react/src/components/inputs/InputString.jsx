import { getDefault } from "./../../utils/commonUtils";

const InputString = (props) => {

    return (
        <div className="form-input-div" key={props.index}>
            <label htmlFor={"field-" + props.index} className="input-label">
                {props.title}
            </label>
            <input
                type={"text"}
                id={"field-" + props.index}
                className="form-input"
                defaultValue={getDefault(props)}
                required={props.mandatory}
                placeholder="Text input"
                onChange={props.onChange}
            />
        </div>
    );
};

InputString.defaultProps = {
    key:'',
    title:'',
    mandatory:'',
    value:'',
    default_value:'',
    onChange: () => {},
}

export default InputString