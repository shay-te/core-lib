import React from 'react';
import Button from '@mui/material/Button';

import './FormButton.scss'
import { useDispatch } from 'react-redux';

const FormButton = (props) => {
    const dispatch = useDispatch()
    return(
        <button className="form-button" onClick={() => dispatch(props.onClick())} variant="contained">{props.label}</button>
    )
}

FormButton.defaultProps = {
    label:'',
    fieldKey:'',
    onClick: () => {},
    keyObj: Object,
}

export default FormButton