import { getBoolean } from '../utils/commonUtils';

export const entityFields = (path, yamlData) => {
    const fields = []
    const dbConn = []
    const pathSplit = path.split('.')
    const CoreLibName = pathSplit.at(0)
    const entity = pathSplit.at(pathSplit.indexOf('data') + 2)
    const dbConnection = pathSplit.at(pathSplit.indexOf('data') + 1)
    const dbConnections = Object.keys(yamlData[CoreLibName]['config']['data'])
    const keyPrefix = CoreLibName + '.data_layers.data.' + dbConnection + '.' + entity
    const entities = yamlData[CoreLibName]['data_layers']['data']
    const entityList = Object.keys(entities[dbConnection])
    dbConnections.forEach(conn => {
        dbConn.push(conn)
    })
    fields.push({
        title: "DB Entity Name",
        type: "string",
        default_value: "",
        value: entity,
        mandatory: true,
        key: keyPrefix,
        id: `entityName_${dbConnection}_${entityList.indexOf(entity)}`
        // validatorCallback: validateFunc,
    });
    if (entities[dbConnection][entity]["columns"]) {
        Object.keys(entities[dbConnection][entity]["columns"]).map((column, index) =>
            fields.push(
                {
                    title: "Column Name",
                    type: "string",
                    default_value: "",
                    value: column,
                    mandatory: true,
                    key: keyPrefix + '.columns.' + column,
                    id: `column_${entity}_${index}`
                    // validatorCallback: validateFunc,
                },
                {
                    title: "Column Type",
                    type: "enum",
                    default_value: "VARCHAR",
                    value: entities[dbConnection][entity]["columns"][column]["type"],
                    mandatory: true,
                    options: ["VARCHAR", "BOOLEAN", "INTEGER"],
                    key: keyPrefix + '.columns.' + column + '.type',
                },
                {
                    title: "Column Default",
                    type: "string",
                    default_value: "",
                    value: entities[dbConnection][entity]["columns"][column][
                        "default"
                    ],
                    mandatory: false,
                    key: keyPrefix + '.columns.' + column + '.default',
                    // validatorCallback: validateFunc,
                }
            )
        );
    }
    if(entities[dbConnection][entity]["is_soft_delete"]){
        fields.push({
            title: "Is Soft Delete",
            type: "boolean",
            default_value: true,
            value: getBoolean(entities[dbConnection][entity]["is_soft_delete"]),
            mandatory: true,
            key: keyPrefix + '.is_soft_delete',
            // validatorCallback: validateFunc,
        },
        {
            title: "Is Soft Delete Token",
            type: "boolean",
            default_value: true,
            value: getBoolean(entities[dbConnection][entity]["is_soft_delete_token"]),
            mandatory: true,
            key: keyPrefix + '.is_soft_delete_token',
            // validatorCallback: validateFunc,
        });
    }
    return fields
};
