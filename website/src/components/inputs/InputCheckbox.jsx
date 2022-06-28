import React from 'react'

const InputCheckbox = (props) => {
    const fieldId = props.keyObj.toString(["checkbox", props.fieldKey])
    return (
        <div className="form-input-div">
            <label className="input-label">{props.title}</label>
            <div key={props.fieldKey}>
                    <input
                        type='checkbox'
                        id={fieldId}
                        name={fieldId}
                        value={props.value}
                        defaultChecked={
                            props.value || props.default_value
                        }
                        onChange={props.onChange}
                    />
                </div>
        </div>
    );
};

InputCheckbox.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    onChange: () => {},
    keyObj: Object,
}

export default InputCheckbox