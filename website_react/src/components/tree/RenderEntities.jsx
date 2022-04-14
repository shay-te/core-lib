import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { hideContents } from "../utils/commonUtils";

const RenderEntities = () => {
	const entities = useSelector((state) => state.treeData.entities);
    const dispatch = useDispatch()

    const setFormField = (dbConn, entity) => {
        const fields = []
        fields.push({
            title: "DB Connection",
            type: "string",
            default_value: '',
            value: entities[dbConn][entity]['db_connection'],
            mandatory: true,
            // validatorCallback: validateFunc,
        })
        if(entities[dbConn][entity].hasOwnProperty('columns')){
            Object.keys(entities[dbConn][entity]['columns']).map((column) => (
                fields.push({
                    title: "Column Name",
                    type: 'string',
                    default_value: '',
                    value: column,
                    mandatory: true,
                    // validatorCallback: validateFunc,
                },
                {
                    title: "Column Type",
                    type: "enum",
                    default_value: 'VARCHAR',
                    value: entities[dbConn][entity]['columns'][column]['type'],
                    mandatory: true,
                    options: [
                        "VARCHAR",
                        "BOOLEAN",
                        "INTEGER",
                    ],
                },
                {
                    title: "Column Default",
                    type: 'string',
                    default_value: '',
                    value: entities[dbConn][entity]['columns'][column]['default'],
                    mandatory: false,
                    // validatorCallback: validateFunc,
                })
            ))
        }
        if(entities[dbConn][entity].hasOwnProperty('is_soft_delete')){
            fields.push({
                title: "Is Soft Delete",
                type: "boolean",
                default_value: true,
                value: entities[dbConn][entity]['is_soft_delete'],
                mandatory: true,
                // validatorCallback: validateFunc,
            })
        }
        if(entities[dbConn][entity].hasOwnProperty('is_soft_delete_token')){
            fields.push({
                title: "Is Soft Delete Token",
                type: "boolean",
                default_value: true,
                value: entities[dbConn][entity]['is_soft_delete_token'],
                mandatory: true,
                // validatorCallback: validateFunc,
            })
        }

        dispatch(setFields(fields))
    }

    const RenderChildNodes = () => {
        return Object.keys(entities).map((dbConn) => {
            return (
                <div
                    className="node-title"
                    key={dbConn}
                    id={dbConn}
                    onClick={(e) => hideContents(e)}
                >
                    {dbConn}
                    {Object.keys(entities[dbConn]).map((entity) => {
                        return entity !== "migrate" ? (
                            <div
                                className="node-child"
                                key={entity}
                                id={dbConn + "_" + entity}
                                onClick={() => setFormField(dbConn, entity)}
                            >
                                {entity}
                            </div>
                        ) : (
                            ""
                        );
                    })}
                </div>
            );
        })
    }

	return (
		<div
			className="node-title"
			id="db-entites"
			onClick={(e) => hideContents(e)}
		>
			DB Entities
			<RenderChildNodes/>
		</div>
	);
};

export default RenderEntities;
