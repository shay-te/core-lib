export const entityFields = (dbConnection, entity, CoreLibName, dbConnections, yamlData) => {
    const fields = []
    const dbConn = []
    const keyPrefix = CoreLibName + '.data_layers.data.' + dbConnection + '.' + entity
    const entities = yamlData[CoreLibName]['data_layers']['data']
    dbConnections.map(conn => {
        dbConn.push(conn.name)
    })
    fields.push({
        title: "DB Entity Name",
        type: "string",
        default_value: "",
        value: entity,
        mandatory: true,
        // validatorCallback: validateFunc,
    },
    {
        title: "DB Connection",
        type: "dropdown",
        default_value: "",
        value: entities[dbConnection][entity]["db_connection"],
        mandatory: true,
        options: dbConn,
        key: keyPrefix + '.db_connection',
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
                key: keyPrefix + '.columns',
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
    fields.push({
        title: "Is Soft Delete",
        type: "boolean",
        default_value: true,
        value: entities[dbConnection][entity]["is_soft_delete"],
        mandatory: true,
        key: keyPrefix + '.is_soft_delete',
        // validatorCallback: validateFunc,
    },
    {
        title: "Is Soft Delete Token",
        type: "boolean",
        default_value: true,
        value: entities[dbConnection][entity]["is_soft_delete_token"],
        mandatory: true,
        key: keyPrefix + '.is_soft_delete_token',
        // validatorCallback: validateFunc,
    });
    return fields
};
