import { isPascalCase } from "../utils/validatorUtils";

export const dataAccessFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const dataAccessList = yamlData.core_lib.data_accesses
    const fields = []
    const index = pathSplit.at(pathSplit.indexOf('data_accesses')+1)
    const dataAccess = dataAccessList[index]
    if(!dataAccess){
        return fields
    }
    const connections = yamlData.core_lib.connections
    const entities = yamlData.core_lib.entities
    const connection = ['']
    const entity = ['']
    const keyPrefix = `core_lib.data_accesses.${index}`
    let isSql = false
    connections.forEach(conn => {
        connection.push(conn.key)
        if(dataAccess['connection'] === conn.key){
            if(conn.type.includes('sql')){
                isSql = true
            }
        }
    })
    const connIndex = connection.indexOf(dataAccess['connection'])
    if(dataAccess['connection']){
        entities.forEach(ent => {
            if(dataAccess['connection'] === ent['connection']){
                entity.push(ent.key)
            }
        })
    }
    fields.push({
        title: 'Enter Data Access Name',
        type: 'string',
        default_value: '',
        value: dataAccess.key,
        mandatory: true,
        key: keyPrefix + '.key',
        toolTipTitle: "Edit Data Access Name (PascalCase)",
        validatorCallback: isPascalCase,
    },
    {
        title: 'Connection',
        type: 'dropdown',
        default_value: connection[0],
        value: dataAccess['connection'],
        mandatory: true,
        options: connection,
        key: keyPrefix + '.connection',
        toolTipTitle: "Select connection for data access",
    })
    if(dataAccess['connection']){
        if(connections[connIndex - 1]['type'].includes('sql')){
            fields.push(
                {
                    title: 'DB Entities',
                    type: 'dropdown',
                    default_value: entity[0],
                    value: dataAccess['entity'],
                    mandatory: true,
                    options: entity,
                    key: keyPrefix + '.entity',
                    toolTipTitle: "Select DB entity for data access",
                },
            )
        }
    }
    
    fields.push(
        {
            title: 'Functions',
            type: 'functions',
            default_value: '',
            value: dataAccess.functions,
            mandatory: true,
            key: `${keyPrefix}.functions`,
        }
    )
    if(isSql){
        fields.push({
            title: 'Is CRUD?',
            type: 'boolean',
            default_value: false,
            value: dataAccess['is_crud'],
            mandatory: true,
            key: keyPrefix + '.is_crud',
            toolTipTitle: {yes: "Will implement CRUD for this Data Access", no: "Will not implement CRUD for this Data Access"},
        })
        if(dataAccess['is_crud']){
            fields.push({
                title: 'Is CRUD Soft Delete?',
                type: 'boolean',
                default_value: false,
                value: dataAccess['is_crud_soft_delete'],
                mandatory: true,
                key: keyPrefix + '.is_crud_soft_delete',
                toolTipTitle: {yes: "Will implement CRUD Soft Delete for this Data Access", no: "Will not implement CRUD Soft Delete for this Data Access"},
            })
        }
        if(dataAccess['is_crud_soft_delete']){
            fields.push({
                title: 'Is CRUD Soft Delete Token?',
                type: 'boolean',
                default_value: false,
                value: dataAccess['is_crud_soft_delete_token'],
                mandatory: true,
                key: keyPrefix + '.is_crud_soft_delete_token',
                toolTipTitle: {yes: "Will implement CRUD Soft Delete Token for this Data Access", no: "Will not implement CRUD Soft Delete Token for this Data Access"},
            })
        }
    }
    return fields
};
