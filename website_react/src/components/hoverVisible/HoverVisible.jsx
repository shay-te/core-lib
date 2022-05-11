import { useState } from "react";
import "./HoverVisible.scss";

const HoverVisible = (props) => {
	const [visible, setVisible] = useState(false);
	const [active, setActive] = useState(false)

	return (
		<div
			onMouseEnter={() => setVisible(true)}
			onMouseLeave={() => setVisible(false)}
			onMouseOver={() => setVisible(true)}
			className={["hover-root", active ? "active" : ""].join(' ')}
		>
			<div onClick={props.onTitleClick.bind(this, props.path)}>
				{props.icon} {props.title}
			</div>
			<div onClick={props.onImageClick.bind(this, props.path)}>
				<img
					alt={"hover img"}
					src={props.image}
					className={[
						"hover-img",
						visible ? "visible" : "hidden",
					].join(" ")}
				/>
			</div>
		</div>
	);
};

HoverVisible.defaultProps = {
	title: "",
	image: "",
	path: "",
	icon: "",
	onClick: () => {},
	onImageClick: () => {},
	onTitleClick: () => {},
};

export default HoverVisible;
