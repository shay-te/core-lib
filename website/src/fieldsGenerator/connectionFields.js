import { getBoolean, getENVValue } from '../utils/commonUtils';

export const connectionFields = (path, yamlData) => {
    const fields = [];
    const pathSplit = path.split('.')
    const connections =  yamlData.core_lib.connections
    const index = pathSplit.at(pathSplit.indexOf('connections')+1)
    const connection = connections[index] 
    const keyPrefix = `core_lib.connections.${index}`
    fields.push(
        {
            title: "What is the name of the DB connection?",
            type: "string",
            default_value: null,
            value: connection.key,
            mandatory: true,
            key: keyPrefix + '.key',
            // validatorCallback: validateFunc,
        },
        {
            title: "Select DB connection",
            type: "enum",
            mandatory: true,
            value: connection["url"]["protocol"],
            // validatorCallback: validateFunc,
            options: [
                "SQLite",
                "Postgresql",
                "MySQL",
                "Oracle",
                "MSSQL",
                "Firebird",
                "Sybase",
            ],
            key: keyPrefix + '.url.protocol',
        }
    );
    if (connection["url"]["protocol"].toLowerCase() !== "mongodb") {
        fields.push(
            {
                title: "Do you want to log queries?",
                type: "boolean",
                default_value: false,
                value: connection["log_queries"],
                mandatory: true,
                key: keyPrefix + '.log_queries',
                // validatorCallback: validateFunc,
            },
            {
                title: "Do you want create Database?",
                type: "boolean",
                default_value: true,
                value: connection["create_db"],
                mandatory: true,
                key: keyPrefix + '.create_db',
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter the pool recycle time",
                type: "integer",
                default_value: 3200,
                value: connection["session"]["pool_recycle"],
                mandatory: true,
                key: keyPrefix + '.session.pool_recycle',
                // validatorCallback: validateFunc,
            },
            {
                title: "Do you want to set pool pre ping?",
                type: "boolean",
                default_value: false,
                value: getBoolean(connection["session"]["pool_pre_ping"]),
                mandatory: true,
                key: keyPrefix + '.session.pool_pre_ping',
                // validatorCallback: validateFunc,
            }
        );
    }

    if (connection["url"]["protocol"].toLowerCase() !== "sqlite" ) {
        const envPrefix = `core_lib.env.${connection.key.toUpperCase()}`
        fields.push(
            {
                title: "Enter the port no. of your DB",
                type: "integer",
                default_value: null,
                value: getENVValue(connection["url"]["port"], yamlData),
                mandatory: true,
                key: `${keyPrefix}.url.port`,
                env: `${envPrefix}_PORT`,
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter host of your DB",
                type: "string",
                default_value: "localhost",
                value: getENVValue(connection["url"]["host"], yamlData),
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
                    connection["url"]["username"], yamlData
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
                    connection["url"]["password"], yamlData
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