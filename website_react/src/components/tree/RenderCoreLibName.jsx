import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { hideContents } from "../utils/commonUtils";
import RenderEntities from "./RenderEntities";

const RenderCoreLibName = () => {
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const dispatch = useDispatch();

	const setFormField = () => {

		const fields = [];
		
        fields.push({
            title: 'Enter Core-Lib name',
            type: 'string',
            default_value: 'UserCoreLib',
            value: CoreLibName,
            mandatory: true,
            // validatorCallback: validateFunc,
        })
		dispatch(setFields(fields));
	};

	return (
		<div
			className="node-title"
			id="db-entites"
			onClick={(e) => hideContents(e)}
		>
			<h2 onClick={() => setFormField()}>{CoreLibName}</h2>
		</div>
	);
};

export default RenderCoreLibName;
