import { getValueAtPath, toSnakeCase } from "../commonUtils"

export const updateEnv = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const target = getValueAtPath(data, steps.slice(0, -1))
    target[steps.at(-1)] = value;
    return data
}

export const updateCache = (path, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const target = getValueAtPath(data, steps.slice(0, -1))
    if (path.includes('type')) {
        if (target.type === 'memory') {
            delete target['url']
            delete  data.core_lib.env[`${target.key.toUpperCase()}_HOST`]
            delete  data.core_lib.env[`${target.key.toUpperCase()}_PORT`]
        }
        if (target.type === 'memcached') {
            if (target.hasOwnProperty('url')) {
                delete target['url']['protocol']
            }
            else {
                target['url'] = {}
            }
            if (!data.core_lib.env) {
                data.core_lib['env'] = {}
            }
            if (!target['url'].hasOwnProperty('host')) {
                target['url']['host'] = '${oc.env:' + target.key.toUpperCase() + '_HOST}'
                data.core_lib.env[`${target.key.toUpperCase()}_HOST`] = 'localhost'
            }
            if (!target['url'].hasOwnProperty('port')) {
                target['url']['port'] = '${oc.env:' + target.key.toUpperCase() + '_PORT}'
                data.core_lib.env[`${target.key.toUpperCase()}_PORT`] = 11211
            }
        }
        if (target.type === 'redis') {
            if (target.hasOwnProperty('url')) {
                delete target['url']['protocol']
            }
            else {
                target['url'] = {}
            }
            if (!data.core_lib.env) {
                data.core_lib['env'] = {}
            }
            if (!target['url'].hasOwnProperty('host')) {
                target['url']['host'] = '${oc.env:' + target.key.toUpperCase() + '_HOST}'
                data.core_lib.env[`${target.key.toUpperCase()}_HOST`] = 'localhost'
            }
            if (!target['url'].hasOwnProperty('port')) {
                target['url']['port'] = '${oc.env:' + target.key.toUpperCase() + '_PORT}'
                data.core_lib.env[`${target.key.toUpperCase()}_PORT`] = 6379
            }
            if (!target['url'].hasOwnProperty('protocol')) {
                target['url']['protocol'] = 'redis'
            }
        }
    }
    return data
}

export const updateConn = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const target = getValueAtPath(data, steps.splice(0, 3))
    const conn = target.key
    if (value.toLowerCase() === 'solr' || value.toLowerCase() === 'neo4j') { 
        const entitySteps = ['core_lib', 'entities']
        let entityTarget = getValueAtPath(data, entitySteps);
        const entities = []
        if(entityTarget.length > 0){
            entityTarget.forEach((entity) => {
                if(entity.connection !== conn){
                    entities.push(entity)
                }
            });
            data.core_lib.entities = entities
            entityTarget = entities.slice(0)
        }
    }
    if (value.toLowerCase() === 'sqlite') {
        target['type'] = 'core_lib.connection.sql_alchemy_connection_registry.SqlAlchemyConnectionRegistry'
        target['config']['url']['protocol'] = value.toLowerCase()
        if (!target.hasOwnProperty('create_db')) {
            target['config']['create_db'] = true
        }
        if (!target.hasOwnProperty('log_queries')) {
            target['config']['log_queries'] = false
        }
        if (!target.hasOwnProperty('session')) {
            const session = {
                pool_recycle: 3200,
                pool_pre_ping: false
            }
            target['config']['session'] = session
        }
        delete target['config']['credentials']
        delete target['config']['url']['username']
        delete data.core_lib.env[conn.toUpperCase() + '_USER']
        delete target['config']['url']['password']
        delete data.core_lib.env[conn.toUpperCase() + '_PASSWORD']
        delete target['config']['url']['host']
        delete data.core_lib.env[conn.toUpperCase() + '_HOST']
        delete target['config']['url']['port']
        delete data.core_lib.env[conn.toUpperCase() + '_PORT']
        delete target['config']['url']['file']
        delete data.core_lib.env[conn.toUpperCase() + '_DB']
    } else {
        if (value.toLowerCase() === 'solr') {
            target['type'] = 'core_lib.connection.solr_connection_registry.SolrConnectionRegistry'
            target['config']['url']['protocol'] = 'http'
            delete target['config']['url']['username']
            delete data.core_lib.env[conn.toUpperCase() + '_USER']
            delete target['config']['url']['password']
            delete data.core_lib.env[conn.toUpperCase() + '_PASSWORD']
            delete target['config']['log_queries']
            delete target['config']['session']
            delete target['config']['create_db']
            delete target['config']['credentials']
        } else if (value.toLowerCase() === 'neo4j') {
            target['type'] = 'core_lib.connection.neo4j_connection_registry.Neo4jConnectionRegistry'
            target['config']['url']['protocol'] = 'neo4j'
            target['config']['credentials'] = {}
            target['config']['credentials']['username'] = '${oc.env:' + target.key.toUpperCase() + '_USER}'
            target['config']['credentials']['password'] = '${oc.env:' + target.key.toUpperCase() + '_PASSWORD}'
            delete target['config']['url']['username']
            delete target['config']['url']['password']
            delete target['config']['url']['file']
            delete target['config']['log_queries']
            delete target['config']['session']
            delete target['config']['create_db']
            delete data.core_lib.env[conn.toUpperCase() + '_DB']
        } else {
            target['type'] = 'core_lib.connection.sql_alchemy_connection_registry.SqlAlchemyConnectionRegistry'
            target['config']['url']['protocol'] = value.toLowerCase()
            delete target['config']['credentials']
            if (!target.hasOwnProperty('create_db')) {
                target['config']['create_db'] = true
            }
            if (!target.hasOwnProperty('log_queries')) {
                target['config']['log_queries'] = false
            }
            if (!target.hasOwnProperty('session')) {
                const session = {
                    pool_recycle: 3200,
                    pool_pre_ping: false
                }
                target['config']['session'] = session
            }
        }

        // #### ENV section
        if (!data.core_lib.env) {
            data.core_lib['env'] = {}
        }
        if (!(value.toLowerCase() === 'solr') && !(value.toLowerCase() === 'neo4j')) {

            if (!target['config']['url'].hasOwnProperty('username')) {
                target['config']['url']['username'] = '${oc.env:' + conn.toUpperCase() + '_USER}'
                data.core_lib.env[conn.toUpperCase() + '_USER'] = 'username'
            }
            if (!target['config']['url'].hasOwnProperty('password')) {
                target['config']['url']['password'] = '${oc.env:' + conn.toUpperCase() + '_PASSWORD}'
                data.core_lib.env[conn.toUpperCase() + '_PASSWORD'] = ''
            }
        }
        if(!(value.toLowerCase() === 'neo4j')){
            if (!target['config']['url'].hasOwnProperty('file')) {
                target['config']['url']['file'] = '${oc.env:' + conn.toUpperCase() + '_DB}'
                data.core_lib.env[conn.toUpperCase() + '_DB'] = conn
            }
        }
        if(value.toLowerCase() === 'neo4j'){
            data.core_lib.env[conn.toUpperCase() + '_USER'] = 'username'
            data.core_lib.env[conn.toUpperCase() + '_PASSWORD'] = ''
        }
        if (!target['config']['url'].hasOwnProperty('host')) {
            target['config']['url']['host'] = '${oc.env:' + conn.toUpperCase() + '_HOST}'
            data.core_lib.env[conn.toUpperCase() + '_HOST'] = 'localhost'
        }
        if (!target['config']['url'].hasOwnProperty('port')) {
            target['config']['url']['port'] = '${oc.env:' + conn.toUpperCase() + '_PORT}'
            data.core_lib.env[conn.toUpperCase() + '_PORT'] = 1234
        }
    }
    return data
}

export const updateSetup = (path, value, yamlData, addOrRemove) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit)
    if (addOrRemove) {
        target.push(value)
    }
    else {
        const index = target.indexOf(value)
        target.splice(index, 1);
    }
    return data
}

export const updateNullable = (path, yamlData, addOrRemove) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.slice(0, -1))
    target.nullable = addOrRemove
    return data
}

export const updateColumnDefault = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.slice(0, -1))
    if (value === '') {
        target.default = null
    } else {
        target.default = value
    }
    return data
}

export const updateFunctionsCheckbox = (path, yamlData, addOrRemove) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.slice(0, -1))
    if (path.includes('cache_invalidate') && !target.hasOwnProperty('cache_key')) {
        return data
    }
    target[pathSplit.at(-1)] = addOrRemove
    return data
}

export const updateFunctionsCache = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.slice(0, -1))
    if (!value) {
        delete target['cache_key']
        delete target['cache_invalidate']
    }
    else {
        target.cache_key = value
        if (!target.hasOwnProperty('cache_invalidate')) {
            target.cache_invalidate = false
        }
    }
    return data
}

export const updateDataAccess = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.splice(0, 3))
    const connSteps = ['core_lib', 'connections']
    const connTarget = getValueAtPath(data, connSteps)
    let connData = {}
    if (target.connection){
        connTarget.forEach(conn => {
            if (conn.key === target.connection){
                connData = conn
            }
        })
    }
    if(path.includes('.connection')){
        if (JSON.stringify(connData) !== '{}' && !connData.type.includes('sql')){
            delete target['entity']
            delete target['is_crud']
            delete target['is_crud_soft_delete']
            delete target['is_crud_soft_delete_token']
        }
        if (!value){
            delete target['connection']
            delete target['entity']
        }
        return data
    }
    if(path.includes('.entity')){
        if (!value){
            delete target['entity']
        }
        return data
    }
    if(path.includes('.is_crud_soft_delete_token')){
        if(value){
            target['is_crud'] = true
            target['is_crud_soft_delete'] = true
        } else {
            delete target['is_crud_soft_delete_token']
        }
        return data
    } else if(path.includes('.is_crud_soft_delete')){
        if(value){
            target['is_crud'] = true
        } else {
            delete target['is_crud_soft_delete']
            delete target['is_crud_soft_delete_token']
        }
        return data
    } else if(path.includes('.is_crud')) {
        if(!value){
            delete target['is_crud']
            delete target['is_crud_soft_delete']
            delete target['is_crud_soft_delete_token']
        }
        return data
    }
    return data
}

export const updateService = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.splice(0, 3))
    if(path.includes('.data_access')){
        if (!value){
            delete target['data_access']
        }
        return data
    }
    return data
}

export const updateJobs = (value, oldValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const jobsSteps = ['core_lib', 'jobs']
    const jobsTarget = getValueAtPath(data, jobsSteps)
    jobsTarget.forEach((job, index) => {
        jobsTarget[index]['handler']['_target_'] = jobsTarget[index]['handler']['_target_'].replaceAll(toSnakeCase(oldValue), toSnakeCase(value))
    })
    return data
}