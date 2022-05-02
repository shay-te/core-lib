export const dataAccessFields = (daName, CoreLibName, dbConnections, dataAccess) => {
    const fields = []
    const dbConn = []
    const keyPrefix = CoreLibName + '.data_layers.data_access.' + daName
    dbConnections.map(conn => {
        dbConn.push(conn.name)
    })
    fields.push({
        title: "Data Access Name",
        type: "string",
        default_value: '',
        value: daName,
        mandatory: true,
        target: 'updateDataAccessName',
        // validatorCallback: validateFunc,
    },
    {
        title: "DB Connection",
        type: "dropdown",
        default_value: '',
        value: dataAccess[daName]['db_connection'],
        mandatory: true,
        options: dbConn,
        key: keyPrefix + '.db_connection',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is CRUD?",
        type: "boolean",
        default_value: false,
        value: dataAccess[daName]['is_crud'],
        mandatory: true,
        key: keyPrefix + '.is_crud',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is CRUD Soft Delete?",
        type: "boolean",
        default_value: false,
        value: dataAccess[daName]['is_crud_soft_delete'],
        mandatory: true,
        key: keyPrefix + '.is_crud_soft_delete',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is CRUD Soft Delete Token?",
        type: "boolean",
        default_value: false,
        value: dataAccess[daName]['is_crud_soft_delete_token'],
        mandatory: true,
        key: keyPrefix + '.is_crud_soft_delete_token',
        // validatorCallback: validateFunc,
    })
    return fields
};
