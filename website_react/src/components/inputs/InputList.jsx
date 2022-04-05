const InputList = (props) => {
    return (
        <div className="form-input-div" key={props.index}>
            <label className="input-label">{props.formFields.title}</label>
            {props.formFields.options.map((value, index) => {
                return (
                    <div key={index}>
                        <input
                            type={
                                props.formFields.multiple_selection
                                    ? "checkbox"
                                    : "radio"
                            }
                            id={value + props.index}
                            name={"list" + props.index}
                            value={value}
                            defaultChecked={
                                value === props.formFields.default_value
                            }
                        />
                        <label htmlFor={value + props.index}>{value}</label>
                    </div>
                );
            })}
        </div>
    );
};

export default InputList