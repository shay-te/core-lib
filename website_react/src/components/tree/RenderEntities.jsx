import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { hideContents } from "../utils/commonUtils";

const RenderEntities = (props) => {
	const entities = useSelector((state) => state.treeData.entities);
    const [entitesList, setEntitiesList] = useState(props.connection)
	const dispatch = useDispatch();

    console.log(props.connection)

	const setFormField = (dbConn, entity) => {
		// const fields = [];
		// fields.push({
		// 	title: "DB Connection",
		// 	type: "string",
		// 	default_value: "",
		// 	value: entities[dbConn][entity]["db_connection"],
		// 	mandatory: true,
		// 	// validatorCallback: validateFunc,
		// });
		// Object.keys(entities[dbConn][entity]["columns"]).map((column) =>
		// 	fields.push(
		// 		{
		// 			title: "Column Name",
		// 			type: "string",
		// 			default_value: "",
		// 			value: column,
		// 			mandatory: true,
		// 			// validatorCallback: validateFunc,
		// 		},
		// 		{
		// 			title: "Column Type",
		// 			type: "enum",
		// 			default_value: "VARCHAR",
		// 			value: entities[dbConn][entity]["columns"][column]["type"],
		// 			mandatory: true,
		// 			options: ["VARCHAR", "BOOLEAN", "INTEGER"],
		// 		},
		// 		{
		// 			title: "Column Default",
		// 			type: "string",
		// 			default_value: "",
		// 			value: entities[dbConn][entity]["columns"][column][
		// 				"default"
		// 			],
		// 			mandatory: false,
		// 			// validatorCallback: validateFunc,
		// 		}
		// 	)
		// );
		// fields.push({
		// 	title: "Is Soft Delete",
		// 	type: "boolean",
		// 	default_value: true,
		// 	value: entities[dbConn][entity]["is_soft_delete"],
		// 	mandatory: true,
		// 	// validatorCallback: validateFunc,
		// });
		// fields.push({
		// 	title: "Is Soft Delete Token",
		// 	type: "boolean",
		// 	default_value: true,
		// 	value: entities[dbConn][entity]["is_soft_delete_token"],
		// 	mandatory: true,
		// 	// validatorCallback: validateFunc,
		// });

		// dispatch(setFields(fields));
	};

	const RenderChildNodes = () => {	
		console.log(props.connection, entities)	
		if(entities && entities.hasOwnProperty(props.connection)){
			return Object.keys(entities[props.connection]).map((entityName) => {
				const key = `${props.connection}_${entityName}`
				return entityName !== "migrate" ? (
					<div
						className="node-child"
						key={key}
						id={key}
						onClick={() => setFormField(props.connection, entityName)}
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
		<div
			className="node-title"
			id="db-entites"
			onClick={(e) => hideContents(e)}
		>
			Entities
			<RenderChildNodes/>
		</div>
	);
};

RenderEntities.defaultProps = {
	connection: ''
}

export default RenderEntities;
