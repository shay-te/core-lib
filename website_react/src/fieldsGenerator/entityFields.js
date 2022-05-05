import { getBoolean } from '../utils/commonUtils';

export const entityFields = (path, yamlData) => {
    const fields = []
    const dbConn = []
    const path_split = path.split('.')
    const CoreLibName = path_split.at(0)
    const entity = path_split.at(-1) 
    const dbConnection = path_split.at(-2) 
    const dbConnections = Object.keys(yamlData[CoreLibName]['config']['data'])
    const entities = yamlData[CoreLibName]['data_layers']['data']
    dbConnections.forEach(conn => {
        dbConn.push(conn)
    })
    fields.push({
        title: "DB Entity Name",
        type: "string",
        default_value: "",
        value: entity,
        mandatory: true,
        key: path + '.entityName',
        // validatorCallback: validateFunc,
    },
    {
        title: "DB Connection",
        type: "dropdown",
        default_value: "",
        value: entities[dbConnection][entity]["db_connection"],
        mandatory: true,
        options: dbConn,
        key: path + '.db_connection',
        // validatorCallback: validateFunc,
    });
    Object.keys(entities[dbConnection][entity]["columns"]).map((column) =>
        fields.push(
            {
                title: "Column Name",
                type: "string",
                default_value: "",
                value: column,
                mandatory: true,
                key: path + '.columns.' + column,
                // validatorCallback: validateFunc,
            },
            {
                title: "Column Type",
                type: "enum",
                default_value: "VARCHAR",
                value: entities[dbConnection][entity]["columns"][column]["type"],
                mandatory: true,
                options: ["VARCHAR", "BOOLEAN", "INTEGER"],
                key: path + '.columns.' + column + '.type',
            },
            {
                title: "Column Default",
                type: "string",
                default_value: "",
                value: entities[dbConnection][entity]["columns"][column][
                    "default"
                ],
                mandatory: false,
                key: path + '.columns.' + column + '.default',
                // validatorCallback: validateFunc,
            }
        )
    );
    fields.push({
        title: "Is Soft Delete",
        type: "boolean",
        default_value: true,
        value: getBoolean(entities[dbConnection][entity]["is_soft_delete"]),
        mandatory: true,
        key: path + '.is_soft_delete',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is Soft Delete Token",
        type: "boolean",
        default_value: true,
        value: getBoolean(entities[dbConnection][entity]["is_soft_delete_token"]),
        mandatory: true,
        key: path + '.is_soft_delete_token',
        // validatorCallback: validateFunc,
    });
    return fields
};
