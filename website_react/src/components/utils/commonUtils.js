export const getDefault = (props) => {
    if(props.value===undefined) return props.default_value
    else return props.value
}

export const hideContents = (e) => {
    e.target.querySelectorAll("div").forEach((child) => {
        child.classList.toggle("hide");
    });
};