import React from 'react'

const InputInteger = (props) => {
    const fieldId = props.keyObj.toString(["integer", props.fieldKey])
    return (
        <div className="form-input-div">
            <label htmlFor={fieldId} className="input-label">
                {props.title}
            </label>
            <input
                type={"number"}
                id={fieldId}
                className="form-input"
                defaultValue={props.value || props.default_value}
                required={props.mandatory}
                placeholder={props.title}
                onChange={props.onChange}
            />
        </div>
    );
};

InputInteger.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    onChange: () => {},
    keyObj: Object,
}

export default InputInteger