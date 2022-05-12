import { getBoolean } from "../utils/commonUtils";

export const dataAccessFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const CoreLibName = pathSplit.at(0)
    const daName = pathSplit.at(pathSplit.indexOf('data_access')+1) 
    const dbConnections = Object.keys(yamlData[CoreLibName]['config']['data'])
    const fields = []
    const dbConn = []
    const keyPrefix = CoreLibName + '.data_layers.data_access.' + daName
    const dataAccess = yamlData[CoreLibName]['data_layers']['data_access'][daName]
    const daList = Object.keys(yamlData[CoreLibName]['data_layers']['data_access'])
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
        id: `dataAccess_${daList.indexOf(daName)}`
        // validatorCallback: validateFunc, onchange validator, predefined validation func for each types
    },
    {
        title: "DB Connection",
        type: "dropdown",
        default_value: dbConn[0],
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
