const InputString = (props) => {
    return (
        <div className="form-input-div" key={props.index}>
            <label htmlFor={"field-" + props.index} className="input-label">
                {props.formFields.title}
            </label>
            <input
                type={"text"}
                id={"field-" + props.index}
                className="form-input"
                defaultValue={props.formFields.default_value}
                required={props.formFields.mandatory}
                placeholder="Text input"
            />
        </div>
    );
};

export default InputString