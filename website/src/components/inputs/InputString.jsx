import React from 'react'

const InputString = (props) => {
    const getDefault = () => {
        if(props.value===undefined) return props.default_value
        else return props.value
    }
    const fieldId = props.keyObj.toString(["field", props.fieldKey])
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <label htmlFor={fieldId} className="input-label">
                {props.title}
            </label>
            <input
                type={"text"}
                id={fieldId}
                className="form-input"
                defaultValue={getDefault()}
                required={props.mandatory}
                placeholder={props.title}
                onChange={props.onChange}
            />
        </div>
    );
};

InputString.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:'',
    value:'',
    default_value:'',
    onChange: () => {},
    keyObj: Object,
}

export default InputString