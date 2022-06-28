import React from 'react'

const InputENUM = (props) => {

    const items = props.options.map((value, index) => {
        const fieldId = props.keyObj.toString(["enum", props.fieldKey])
        return (<div key={value}>
            <input
                type={props.multiple_selection ? "checkbox" : "radio"}
                id={fieldId}
                name={fieldId}
                value={value}
                defaultChecked={
                    value.toLowerCase() === (props.value.toLowerCase() || props.default_value.toLowerCase())
                }
                onChange={props.onChange}
            />
            <label htmlFor={fieldId}>{value}</label>
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
    keyObj: Object,
}

export default InputENUM