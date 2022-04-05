const InputInteger = (props) => {
    return (
        <div className="form-input-div" key={props.index}>
            <label htmlFor={"field-" + props.index} className="input-label">
                {props.formFields.title}
            </label>
            <input
                type={"number"}
                id={"field-" + props.index}
                className="form-input"
                defaultValue={props.formFields.default_value}
                required={props.formFields.mandatory}
                placeholder="Number input"
            />
        </div>
    );
};

export default InputInteger