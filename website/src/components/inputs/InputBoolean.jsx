import React from 'react'

const InputBoolean = (props) => {
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <label className="input-label">{props.title}</label>
            <div>
                <input
                    type="radio"
                    id={props.keyObj.toString(["true", props.fieldKey])}
                    name={props.keyObj.toString(["bool", props.fieldKey])}
                    value={true}
                    defaultChecked={props.value || props.default_value}
                    required={props.mandatory}
                    onChange={props.onChange}
                />
                <label htmlFor={props.keyObj.toString(["true", props.fieldKey])}>Yes</label>
            </div>

            <div>
                <input
                    type="radio"
                    id={props.keyObj.toString(["false", props.fieldKey])}
                    name={props.keyObj.toString(["bool", props.fieldKey])}
                    value={false}
                    defaultChecked={!(props.value || props.default_value)}
                    required={props.mandatory}
                    onChange={props.onChange}
                />
                <label htmlFor={props.keyObj.toString(["false", props.fieldKey])}>No</label>
            </div>
        </div>
    );
};

InputBoolean.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:false,
    default_value:false,
    onChange: () => {},
}

export default InputBoolean