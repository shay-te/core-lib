import Form from "./../components/form/Form";
import Tree from "./../components/tree/Tree";
import { updateFields } from "./../components/slices/treeSlice";
import { useDispatch } from "react-redux";

const Editor = () => {
	const dispatch = useDispatch();

	const onFieldChange = (field, e) => {
		if (field.key) {
			dispatch(
				updateFields({
					path: field.key,
					value: e.target.value,
					env: field.env,
				})
			);
		}
	};

	return (
		<div className="home">
			<Tree key={"tree"} />
			<Form onChange={onFieldChange} />
		</div>
	);
};

export default Editor;
