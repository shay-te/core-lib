import React from 'react'

const InputList = (props) => {

    const RenderItems = () => {
        const fieldId = props.keyObj.toString(["list", props.fieldKey])
        return props.options.map((value, index) => {
            return (
                <div key={index}>
                    <input
                        type={
                            props.multiple_selection
                                ? "checkbox"
                                : "radio"
                        }
                        id={fieldId}
                        name={fieldId}
                        value={value}
                        defaultChecked={
                            props.value.includes(value) || props.default_value.includes(value)
                        }
                        onChange={props.onChange}
                    />
                    <label htmlFor={fieldId}>{value}</label>
                </div>
            );
        })
    }

    return (
        <div className="form-input-div">
            <label className="input-label">{props.title}</label>
            <RenderItems/>
        </div>
    );
};

InputList.defaultProps = {
    fieldKey:'',
    title:'',
    mandatory:false,
    value:'',
    default_value:'',
    options: [],
    multiple_selection: false,
    onChange: () => {},
    keyObj: Object,
}

export default InputList