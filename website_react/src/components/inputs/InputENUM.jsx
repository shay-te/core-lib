import { getDefault } from "../utils/commonUtils";

const InputENUM = (props) => {

    const items = props.options.map((value, index) => {
        return (<div key={value}>
            <input
                type={props.multiple_selection ? "checkbox" : "radio"}
                id={value + props.index}
                name={"enum" + props.index}
                value={value}
                defaultChecked={
                    value.toLowerCase() === getDefault(props).toLowerCase()
                }
                onChange={props.onChange}
            />
            <label htmlFor={value + props.index}>{value}</label>
        </div>);
    });

    return (
        <div className="form-input-div">
            <label className="input-label">{props.title}</label>
            <div>{items}</div>
        </div>
    );
};

InputENUM.defaultProps = {
    title: '',
    options: {},
}

export default InputENUM