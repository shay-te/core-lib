import { getDefault } from "./../../utils/commonUtils";

const InputBoolean = (props) => {
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <label className="input-label">{props.title}</label>
            <div>
                <input
                    type="radio"
                    id={"true" + props.fieldKey}
                    name={"bool" + props.fieldKey}
                    value={true}
                    defaultChecked={getDefault(props)}
                    required={props.mandatory}
                    onChange={props.onChange}
                />
                <label htmlFor={"true" + props.fieldKey}>Yes</label>
            </div>

            <div>
                <input
                    type="radio"
                    id={"false" + props.fieldKey}
                    name={"bool" + props.fieldKey}
                    value={false}
                    defaultChecked={!getDefault(props)}
                    required={props.mandatory}
                    onChange={props.onChange}
                />
                <label htmlFor={"false" + props.fieldKey}>No</label>
            </div>
        </div>
    );
};

InputBoolean.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:false,
    default_value:false,
    onChange: () => {},
}

export default InputBoolean