import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";

const RenderEntities = (props) => {
	const entities = useSelector((state) => state.treeData.entities);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const dispatch = useDispatch();

	const setFormFieldEntity = (dbConn, entity) => {
		const fields = [];
		const keyPrefix = CoreLibName + '.data_layers.data.' + dbConn + '.' + entity
		fields.push({
			title: "DB Entity Name",
			type: "string",
			default_value: "",
			value: entity,
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "DB Connection",
			type: "dropdown",
			default_value: "",
			value: entities[dbConn][entity]["db_connection"],
			mandatory: true,
			options: Object.keys(dbConnections),
			key: keyPrefix + '.db_connection',
			// validatorCallback: validateFunc,
		});
		Object.keys(entities[dbConn][entity]["columns"]).map((column) =>
			fields.push(
				{
					title: "Column Name",
					type: "string",
					default_value: "",
					value: column,
					mandatory: true,
					key: keyPrefix + '.columns',
					// validatorCallback: validateFunc,
				},
				{
					title: "Column Type",
					type: "enum",
					default_value: "VARCHAR",
					value: entities[dbConn][entity]["columns"][column]["type"],
					mandatory: true,
					options: ["VARCHAR", "BOOLEAN", "INTEGER"],
					key: keyPrefix + '.columns.' + column + '.type',
				},
				{
					title: "Column Default",
					type: "string",
					default_value: "",
					value: entities[dbConn][entity]["columns"][column][
						"default"
					],
					mandatory: false,
					key: keyPrefix + '.columns.' + column + '.default',
					// validatorCallback: validateFunc,
				}
			)
		);
		fields.push({
			title: "Is Soft Delete",
			type: "boolean",
			default_value: true,
			value: entities[dbConn][entity]["is_soft_delete"],
			mandatory: true,
			key: keyPrefix + '.is_soft_delete',
			// validatorCallback: validateFunc,
		},
		{
			title: "Is Soft Delete Token",
			type: "boolean",
			default_value: true,
			value: entities[dbConn][entity]["is_soft_delete_token"],
			mandatory: true,
			key: keyPrefix + '.is_soft_delete_token',
			// validatorCallback: validateFunc,
		});

		dispatch(setFields(fields));
	};

	const RenderChildNodes = () => {
		if(entities && entities.hasOwnProperty(props.connection)){
			return Object.keys(entities[props.connection]).map((entityName) => {
				const key = `${props.connection}_${entityName}`
				return entityName !== "migrate" ? (
					<div
						className="node-child"
						key={key}
						id={key}
						onClick={() => setFormFieldEntity(props.connection, entityName)}
					>
						{entityName}
					</div>
				) : (
					""
				);
			})
		}
        
    }
    
	return (
		<RenderChildNodes/>
	);
};

RenderEntities.defaultProps = {
	connection: ''
}

export default RenderEntities;
