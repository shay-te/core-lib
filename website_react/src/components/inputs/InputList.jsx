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
                        id={value + props.fieldKey}
                        name={"list" + props.fieldKey}
                        value={value}
                        defaultChecked={
                            props.value.includes(value) || props.default_value.includes(value)
                        }
                        onChange={props.onChange}
                    />
                    <label htmlFor={value + props.fieldKey}>{value}</label>
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
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    options: [],
    multiple_selection: false,
    onChange: () => {},
}

export default InputList