import { getBoolean } from '../utils/commonUtils';

export const dbConnectionFields = (dbConn, CoreLibName, yamlData) => {
    const getENVValue = (envVar) => {
		return yamlData[CoreLibName]["env"][envVar.split(":")[1].slice(0, -1)];
	};
    const fields = [];
    const keyPrefix = CoreLibName + '.config.data.' + dbConn
    const dbConnections =  yamlData[CoreLibName]['config']['data']
    fields.push(
        {
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
            value: dbConnections[dbConn]["url"]["protocol"],
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
            key: keyPrefix + '.url.protocol',
        }
    );
    if (dbConnections[dbConn]["url"]["protocol"] !== "mongodb") {
        fields.push(
            {
                title: "Do you want to log queries?",
                type: "boolean",
                default_value: false,
                value: dbConnections[dbConn]["log_queries"],
                mandatory: true,
                key: keyPrefix + '.log_queries',
                // validatorCallback: validateFunc,
            },
            {
                title: "Do you want create Database?",
                type: "boolean",
                default_value: true,
                value: dbConnections[dbConn]["create_db"],
                mandatory: true,
                key: keyPrefix + '.create_db',
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter the pool recycle time",
                type: "integer",
                default_value: 3200,
                value: dbConnections[dbConn]["session"]["pool_recycle"],
                mandatory: true,
                key: keyPrefix + '.session.pool_recycle',
                // validatorCallback: validateFunc,
            },
            {
                title: "Do you want to set pool pre ping?",
                type: "boolean",
                default_value: false,
                value: getBoolean(dbConnections[dbConn]["session"]["pool_pre_ping"]),
                mandatory: true,
                key: keyPrefix + '.session.pool_pre_ping',
                // validatorCallback: validateFunc,
            }
        );
    }

    if (dbConnections[dbConn]["url"]["protocol"] !== "sqlite") {
        fields.push(
            {
                title: "Enter the port no. of your DB",
                type: "integer",
                default_value: null,
                value: getENVValue(dbConnections[dbConn]["url"]["port"]),
                mandatory: true,
                key: keyPrefix + '.url.port',
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter host of your DB",
                type: "string",
                default_value: "localhost",
                value: getENVValue(dbConnections[dbConn]["url"]["host"]),
                mandatory: true,
                key: keyPrefix + '.url.host',
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter your DB username",
                type: "string",
                default_value: "user",
                value: getENVValue(
                    dbConnections[dbConn]["url"]["username"]
                ),
                mandatory: true,
                key: keyPrefix + '.url.username',
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter your DB password",
                type: "string",
                default_value: null,
                value: getENVValue(
                    dbConnections[dbConn]["url"]["password"]
                ),
                mandatory: true,
                key: keyPrefix + '.url.password',
                // validatorCallback: validateFunc,
            }
        );
    }
    return fields
}