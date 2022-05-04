export const getDefault = (props) => {
    if(props.value===undefined) return props.default_value
    else return props.value
}
