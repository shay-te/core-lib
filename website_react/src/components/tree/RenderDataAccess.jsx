import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { updateDataAccess } from "../slices/treeSlice"
import { hideContents } from "../utils/commonUtils";

const RenderDataAccess = () => {
	const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const dispatch = useDispatch()

	const updateDAName = (oldname) => {
		dispatch(updateDataAccess(oldname))
	}

	const setFormFields = (daName) => {
		const fields = []
		const keyPrefix = CoreLibName + '.data_layers.data_access.' + daName
		fields.push({
            title: "Data Access Name",
            type: "string",
            default_value: '',
			value: daName,
            mandatory: true,
			target: 'updateDataAccessName',
            // validatorCallback: validateFunc,
        },
		{
            title: "DB Connection",
            type: "dropdown",
            default_value: '',
			value: dataAccess[daName]['db_connection'],
            mandatory: true,
			options: Object.keys(dbConnections),
			key: keyPrefix + '.db_connection',
            // validatorCallback: validateFunc,
        },
		{
			title: "Is CRUD?",
			type: "boolean",
			default_value: false,
			value: dataAccess[daName]['is_crud'],
			mandatory: true,
			key: keyPrefix + '.is_crud',
			// validatorCallback: validateFunc,
		},
		{
			title: "Is CRUD Soft Delete?",
			type: "boolean",
			default_value: false,
			value: dataAccess[daName]['is_crud_soft_delete'],
			mandatory: true,
			key: keyPrefix + '.is_crud_soft_delete',
			// validatorCallback: validateFunc,
		},
		{
			title: "Is CRUD Soft Delete Token?",
			type: "boolean",
			default_value: false,
			value: dataAccess[daName]['is_crud_soft_delete_token'],
			mandatory: true,
			key: keyPrefix + '.is_crud_soft_delete_token',
			// validatorCallback: validateFunc,
		})

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
