export const getDefault = (props) => {
    if(props.value===undefined) return props.default_value
    else return props.value
}


export const getBoolean = (value) => {
    if (typeof value === 'boolean') {
        return value;
    }
    if (value && value.trim().toLowerCase() === 'true') {
        return true;
    }
    return false;
}

export const isObject = (obj) => {
    return obj != null && obj.constructor.name === "Object"
}