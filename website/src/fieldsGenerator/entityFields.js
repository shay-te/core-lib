import { getBoolean } from '../utils/commonUtils';

export const entityFields = (path, yamlData) => {
    const fields = []
    const dbConn = []
    const pathSplit = path.split('.')
    const index = pathSplit.at(pathSplit.indexOf('entities') + 1)
    const entity = yamlData.core_lib.entities[index]
    const connections = yamlData.core_lib.connections
    const keyPrefix = `core_lib.entities.${index}`
    connections.forEach(conn => {
        dbConn.push(conn.key)
    })
    fields.push({
        title: "Enter DB Entity Name",
        type: "string",
        default_value: "",
        value: entity.key,
        mandatory: true,
        key: `${keyPrefix}.key`,
        // validatorCallback: validateFunc,
    },
    {
        title: "DB Connection",
        type: "dropdown",
        default_value: dbConn[0],
        value: entity['db_connection'],
        mandatory: true,
        options: dbConn,
        key: keyPrefix + '.db_connection',
        // validatorCallback: validateFunc,
    },
    {
        title: "Columns",
        type: "columns",
        default_value: "",
        value: entity.columns,
        mandatory: true,
        key: `${keyPrefix}.columns`,
        // validatorCallback: validateFunc,
    });
    if(entity.hasOwnProperty('is_soft_delete')){
        fields.push({
            title: "Is Soft Delete",
            type: "boolean",
            default_value: true,
            value: getBoolean(entity["is_soft_delete"]),
            mandatory: true,
            key: keyPrefix + '.is_soft_delete',
            // validatorCallback: validateFunc,
        },
        {
            title: "Is Soft Delete Token",
            type: "boolean",
            default_value: true,
            value: getBoolean(entity["is_soft_delete_token"]),
            mandatory: true,
            key: keyPrefix + '.is_soft_delete_token',
            // validatorCallback: validateFunc,
        });
    }
    return fields
};
