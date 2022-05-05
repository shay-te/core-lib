import { getBoolean } from "../utils/commonUtils";

export const dataAccessFields = (path, yamlData) => {
    const path_split = path.split('.')
    const CoreLibName = path_split.at(0)
    const daName = path_split.at(-2) 
    const dbConnections = Object.keys(yamlData[CoreLibName]['config']['data'])
    const fields = []
    const dbConn = []
    const keyPrefix = CoreLibName + '.data_layers.data_access.' + daName
    const dataAccess = yamlData[CoreLibName]['data_layers']['data_access'][daName]
    dbConnections.forEach(conn => {
        dbConn.push(conn)
    })
    fields.push({
        title: "Data Access Name",
        type: "string",
        default_value: '',
        value: daName,
        mandatory: true,
        key: keyPrefix,
        // validatorCallback: validateFunc,
    },
    {
        title: "DB Connection",
        type: "dropdown",
        default_value: '',
        value: dataAccess['db_connection'],
        mandatory: true,
        options: dbConn,
        key: keyPrefix + '.db_connection',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is CRUD?",
        type: "boolean",
        default_value: false,
        value: getBoolean(dataAccess['is_crud']),
        mandatory: true,
        key: keyPrefix + '.is_crud',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is CRUD Soft Delete?",
        type: "boolean",
        default_value: false,
        value: getBoolean(dataAccess['is_crud_soft_delete']),
        mandatory: true,
        key: keyPrefix + '.is_crud_soft_delete',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is CRUD Soft Delete Token?",
        type: "boolean",
        default_value: false,
        value: getBoolean(dataAccess['is_crud_soft_delete_token']),
        mandatory: true,
        key: keyPrefix + '.is_crud_soft_delete_token',
        // validatorCallback: validateFunc,
    })
    return fields
};
