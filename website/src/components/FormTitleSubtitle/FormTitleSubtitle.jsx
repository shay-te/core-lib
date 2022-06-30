import React from 'react'


const FormTitleSubtitle = (props) => {
    return (
        <div className="form-input-div" key={props.fieldKey}>
            <div className="form-title">
                {props.title}
            </div>
            <div className="form-subtitle">
                {props.subtitle}
            </div>
        </div>
    );
};

FormTitleSubtitle.defaultProps = {
    fieldKey:'',
    title:'',
    subtitle: '',
    keyObj: Object,
}

export default FormTitleSubtitle