import { getDefault } from "./../../utils/commonUtils";

const InputList = (props) => {

    const RenderItems = () => {
        return props.options.map((value, index) => {
            return (
                <div key={index}>
                    <input
                        type={
                            props.multiple_selection
                                ? "checkbox"
                                : "radio"
                        }
                        id={value + props.index}
                        name={"list" + props.index}
                        value={value}
                        defaultChecked={
                            getDefault(props).includes(value)
                        }
                        onChange={props.onChange}
                    />
                    <label htmlFor={value + props.index}>{value}</label>
                </div>
            );
        })
    }

    return (
        <div className="form-input-div">
            <label className="input-label">{props.title}</label>
            <RenderItems/>
        </div>
    );
};

InputList.defaultProps = {
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    options: [],
    multiple_selection: false,
    onChange: () => {},
}

export default InputList