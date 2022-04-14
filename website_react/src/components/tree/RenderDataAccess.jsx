import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { hideContents } from "../utils/commonUtils";

const RenderDataAccess = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const dispatch = useDispatch()

	const setFormFields = (daName) => {
		const fields = []
		fields.push({
            title: "Data Access Name",
            type: "string",
            default_value: '',
			value: daName,
            mandatory: true,
            // validatorCallback: validateFunc,
        })
		fields.push({
            title: "DB Connection",
            type: "string",
            default_value: '',
			value: dataAccess[daName]['db_connection'],
            mandatory: true,
            // validatorCallback: validateFunc,
        })
		if(dataAccess[daName].hasOwnProperty('is_crud')){
			fields.push({
				title: "Is CRUD?",
				type: "boolean",
				default_value: false,
				value: dataAccess[daName]['is_crud'],
				mandatory: true,
				// validatorCallback: validateFunc,
			})
		}
		if(dataAccess[daName].hasOwnProperty('is_crud_soft_delete')){
			fields.push({
				title: "Is CRUD Soft Delete?",
				type: "boolean",
				default_value: false,
				value: dataAccess[daName]['is_crud_soft_delete'],
				mandatory: true,
				// validatorCallback: validateFunc,
			})
		}
		if(dataAccess[daName].hasOwnProperty('is_crud_soft_delete_token')){
			fields.push({
				title: "Is CRUD Soft Delete Token?",
				type: "boolean",
				default_value: false,
				value: dataAccess[daName]['is_crud_soft_delete_token'],
				mandatory: true,
				// validatorCallback: validateFunc,
			})
		}

		dispatch(setFields(fields))
	}

	const RenderChildNodes = () => {
		return Object.keys(dataAccess).map((key) => {
			return <div className="node-child" key={key} onClick={() => setFormFields(key)}>{key}</div>;
		})
	}

	return (
			<div className="node-title" onClick={(e) => hideContents(e)}>Data Access
			<RenderChildNodes/>
            </div>
	);
};

export default RenderDataAccess;
