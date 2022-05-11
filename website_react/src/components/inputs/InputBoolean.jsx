import { getDefault } from "./../../utils/commonUtils";

const InputBoolean = (props) => {
    return (
        <div className="form-input-div" key={props.index}>
            <label className="input-label">{props.title}</label>
            <div>
                <input
                    type="radio"
                    id={"true" + props.index}
                    name={"bool" + props.index}
                    value={true}
                    defaultChecked={getDefault(props)}
                    required={props.mandatory}
                    onChange={props.onChange}
                />
                <label htmlFor={"true" + props.index}>Yes</label>
            </div>

            <div>
                <input
                    type="radio"
                    id={"false" + props.index}
                    name={"bool" + props.index}
                    value={false}
                    defaultChecked={!getDefault(props)}
                    required={props.mandatory}
                    onChange={props.onChange}
                />
                <label htmlFor={"false" + props.index}>No</label>
            </div>
        </div>
    );
};

InputBoolean.defaultProps = {
    title:'',
    mandatory:false,
    value:false,
    default_value:false,
    onChange: () => {},
}

export default InputBoolean