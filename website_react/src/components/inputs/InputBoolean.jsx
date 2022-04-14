import { getDefault } from "../utils/commonUtils";

const InputBoolean = (props) => {
    return (
        <div className="form-input-div" key={props.index}>
            <label className="input-label">{props.title}</label>
            <div>
                <input
                    type="radio"
                    id={"true" + props.index}
                    name={"bool" + props.index}
                    value="true"
                    defaultChecked={getDefault(props)}
                    required={props.mandatory}
                />
                <label htmlFor={"true" + props.index}>Yes</label>
            </div>

            <div>
                <input
                    type="radio"
                    id={"false" + props.index}
                    name={"bool" + props.index}
                    value="false"
                    defaultChecked={!getDefault(props)}
                    required={props.mandatory}
                />
                <label htmlFor={"false" + props.index}>No</label>
            </div>
        </div>
    );
};

export default InputBoolean