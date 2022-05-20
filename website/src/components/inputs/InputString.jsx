import React from 'react'

const InputString = (props) => {
    const getDefault = () => {
        if(props.value===undefined) return props.default_value
        else return props.value
    }
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <label htmlFor={"field-" + props.fieldKey} className="input-label">
                {props.title}
            </label>
            <input
                type={"text"}
                id={"field-" + props.fieldKey}
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
}

export default InputString