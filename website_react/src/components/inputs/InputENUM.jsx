const InputENUM = (props) => {

    const items = props.options.map((value, index) => {
        return (<div key={value}>
            <input
                type={props.multiple_selection ? "checkbox" : "radio"}
                id={value + props.fieldKey}
                name={"enum" + props.fieldKey}
                value={value}
                defaultChecked={
                    value.toLowerCase() === (props.value.toLowerCase() || props.default_value.toLowerCase())
                }
                onChange={props.onChange}
            />
            <label htmlFor={value + props.fieldKey}>{value}</label>
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
    fieldKey:'',
    title:'',
    mandatory: true,
    value:'',
    default_value:'',
    multiple_selection:false,
    options:[],
}

export default InputENUM