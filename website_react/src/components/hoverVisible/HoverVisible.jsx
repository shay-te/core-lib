import './HoverVisible.scss'

const HoverVisible = (props) =>{

    return(
        <div className={['hover-visible', props.isVisible ? 'visible' : ''].join(' ')}>
            {props.children}
        </div>
    )
}

HoverVisible.defaultProps = {
    isVisible: false,
}

export default HoverVisible;