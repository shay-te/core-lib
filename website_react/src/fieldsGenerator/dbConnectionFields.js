import { getBoolean, getENVValue } from '../utils/commonUtils';

export const dbConnectionFields = (path, yamlData) => {
    const fields = [];
    const pathSplit = path.split('.')
    const CoreLibName = pathSplit.at(0)
    const dbConn = pathSplit.at(pathSplit.indexOf('data')+1) 
    const keyPrefix = CoreLibName + '.config.data.' + dbConn
    const dbConnections =  yamlData[CoreLibName]['config']['data']
    const dbConnList = Object.keys(dbConnections)
    fields.push(
        {
            title: "What is the name of the DB connection?",
            type: "string",
            default_value: null,
            value: dbConn,
            mandatory: true,
            key: keyPrefix,
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
    if (dbConnections[dbConn]["url"]["protocol"].toLowerCase() !== "mongodb") {
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

    if (dbConnections[dbConn]["url"]["protocol"].toLowerCase() !== "sqlite" ) {
        const envPrefix =  CoreLibName+'.env.'+dbConn.toUpperCase()
        fields.push(
            {
                title: "Enter the port no. of your DB",
                type: "integer",
                default_value: null,
                value: getENVValue(dbConnections[dbConn]["url"]["port"], yamlData),
                mandatory: true,
                key: `${keyPrefix}.url.port`,
                env: `${envPrefix}_PORT`,
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter host of your DB",
                type: "string",
                default_value: "localhost",
                value: getENVValue(dbConnections[dbConn]["url"]["host"], yamlData),
                mandatory: true,
                key: `${keyPrefix}.url.host`,
                env: `${envPrefix}_HOST`,
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter your DB username",
                type: "string",
                default_value: "user",
                value: getENVValue(
                    dbConnections[dbConn]["url"]["username"], yamlData
                ),
                mandatory: true,
                key: `${keyPrefix}.url.username`,
                env: `${envPrefix}_USER`,
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter your DB password",
                type: "string",
                default_value: null,
                value: getENVValue(
                    dbConnections[dbConn]["url"]["password"], yamlData
                ),
                mandatory: true,
                key: `${keyPrefix}.url.password`,
                env: `${envPrefix}_PASSWORD`,
                // validatorCallback: validateFunc,
            }
        );
    }
    return fields
}