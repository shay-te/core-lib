const InputENUM = (props) => {

    const RenderItems = () => {
        return props.formFields.options.map((value, index) => {
            return (
                <div key={index}>
                    <input
                        type={
                            props.formFields.multiple_selection
                                ? "checkbox"
                                : "radio"
                        }
                        id={value + props.index}
                        name={"enum" + props.index}
                        value={value}
                        defaultChecked={
                            value === props.formFields.default_value
                        }
                    />
                    <label htmlFor={value + props.index}>{value}</label>
                </div>
            );
        })
    } 

    return (
        <div className="form-input-div" key={props.index}>
            <label className="input-label">{props.formFields.title}</label>
            <RenderItems/>
        </div>
    );
};

export default InputENUM