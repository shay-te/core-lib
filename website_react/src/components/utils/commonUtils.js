export const getDefault = (props) => {
    if(props.formFields.value===undefined) return props.formFields.default_value
    else return props.formFields.value
}

export const hideContents = (e) => {
    e.target.querySelectorAll("div").forEach((child) => {
        child.classList.toggle("hide");
    });
};