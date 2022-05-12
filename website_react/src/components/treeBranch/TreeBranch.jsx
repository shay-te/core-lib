import { useState } from "react";
import "./TreeBranch.scss";
import HoverVisible from '../hoverVisible/HoverVisible'

const TreeBranch = (props) => {
	const [visible, setVisible] = useState(false);
	const [active, setActive] = useState(false);

	return (
		<div
			onMouseEnter={() => setVisible(true)}
			onMouseLeave={() => setVisible(false)}
			onMouseOver={() => setVisible(true)}
			className={['tree-branch'].join(' ')}
		>
			<div onClick={props.onTitleClick.bind(this, props.path)}>
				{props.icon} {props.title}
			</div>
			<HoverVisible isVisible={visible}>
				<div onClick={props.onImageClick.bind(this, props.path)}>
					<img
						alt={"hover img"}
						src={props.image}
						className={[
							"hover-img"
						].join(" ")}
					/>
				</div>
			</HoverVisible>
		</div>
	);
};

TreeBranch.defaultProps = {
	title: "",
	image: "",
	path: "",
	icon: "",
	onClick: () => {},
	onImageClick: () => {},
	onTitleClick: () => {},
};

export default TreeBranch;
