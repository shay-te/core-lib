import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { hideContents } from "../utils/commonUtils";
import RenderEntities from "./RenderEntities";

const RenderDBConn = () => {
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const dispatch = useDispatch();

	const setFormField = (dbConn) => {
		console.log(dbConn)

		const fields = [];
		fields.push({
			title: "What is the name of the DB connection?",
			type: "string",
			default_value: null,
			value: dbConn,
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Select DB connection",
			type: "enum",
			mandatory: true,
			value: dbConnections[dbConn]['url']['protocol'],
			// validatorCallback: validateFunc,
			options: [
				"SQLite",
				"Postgresql",
				"MySQL",
				"Oracle",
				"MSSQL",
				"Firebird",
				"Sybase",
				"MongoDB",
			],
		},
		{
			title: "Do you want to log queries?",
			type: "boolean",
			default_value: false,
			value: dbConnections[dbConn]['log_queries'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Do you want create Database?",
			type: "boolean",
			default_value: true,
			value: dbConnections[dbConn]['create_db'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Enter the pool recycle time",
			type: "integer",
			default_value: 3200,
			value: dbConnections[dbConn]['session']['pool_recycle'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Do you want to set pool pre ping?",
			type: "boolean",
			default_value: false,
			value: dbConnections[dbConn]['session']['pool_pre_ping'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Enter the port no. of your DB",
			type: "integer",
			default_value: null,
			value: dbConnections[dbConn]['url']['port'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Enter host of your DB",
			type: "string",
			default_value: "localhost",
			value: dbConnections[dbConn]['url']['host'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Enter your DB username",
			type: "string",
			default_value: "user",
			value: dbConnections[dbConn]['url']['username'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},
		{
			title: "Enter your DB password",
			type: "string",
			default_value: null,
			value: dbConnections[dbConn]['url']['password'],
			mandatory: true,
			// validatorCallback: validateFunc,
		},);

		dispatch(setFields(fields));
	};

	const RenderChildNodes = () => {
		return Object.keys(dbConnections).map((dbConn) => {
			return (
				<div
					className="node-title"
					key={dbConn}
					id={dbConn}
					onClick={(e) => {hideContents(e); setFormField(dbConn)}}
				>
					{dbConn}
					<RenderEntities connection={dbConn}/>
					{/* {Object.keys(entities[dbConn]).map((entity) => {
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
					})} */}
				</div>
			);
		});
	};

	return (
		<div
			className="node-title"
			id="db-entites"
			onClick={(e) => hideContents(e)}
		>
			DB Connections
			<RenderChildNodes />
		</div>
	);
};

export default RenderDBConn;
