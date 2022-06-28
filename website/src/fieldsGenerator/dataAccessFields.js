import { getBoolean } from '../utils/commonUtils';

export const dataAccessFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const dataAccessList = yamlData.core_lib.data_accesses
    const index = pathSplit.at(pathSplit.indexOf('data_accesses')+1)
    const dataAccess = dataAccessList[index]
    const connections = yamlData.core_lib.connections
    const entities = yamlData.core_lib.entities
    const fields = []
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
        // validatorCallback: validateFunc, onchange validator, predefined validation func for each types
    },
    {
        title: 'Connection',
        type: 'dropdown',
        default_value: connection[0],
        value: dataAccess['connection'],
        mandatory: true,
        options: connection,
        key: keyPrefix + '.connection',
        // validatorCallback: validateFunc,
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
            // validatorCallback: validateFunc,
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
            // validatorCallback: validateFunc,
        })
        if(dataAccess['is_crud']){
            fields.push({
                title: 'Is CRUD Soft Delete?',
                type: 'boolean',
                default_value: false,
                value: dataAccess['is_crud_soft_delete'],
                mandatory: true,
                key: keyPrefix + '.is_crud_soft_delete',
                // validatorCallback: validateFunc,
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
                // validatorCallback: validateFunc,
            })
        }
    }
    return fields
};
