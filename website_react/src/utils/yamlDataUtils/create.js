import { toCamelCase, toSnakeCase, getValueAtPath } from "../commonUtils"

export const entity = (dbConn, yamlData, coreLibName) => {
    const newNormalEntity = {
        db_connection: dbConn,
        columns: {
            column_name: {
                type: "VARCHAR",
                default: "",
            },
        },
        is_soft_delete: true,
        is_soft_delete_token: true,
    }

    const newMongoEntity = {
        db_connection: dbConn,
    }

    let newEntity = {}

    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = [coreLibName, 'data_layers', 'data', dbConn]
    const target = getValueAtPath(data, steps)
    const dbConnSteps = [coreLibName, 'config', 'data']
    const dbConns = getValueAtPath(data, dbConnSteps)

    if(dbConns[dbConn]['url']['protocol'] === 'mongodb'){
        newEntity = Object.assign({}, newMongoEntity)
    }else{
        newEntity = Object.assign({}, newNormalEntity)
    }

    if (!target) {
        const newSteps = [coreLibName, 'data_layers', 'data']
        const newTarget = getValueAtPath(data, newSteps)
        newTarget[dbConn] = { [`new_entity`]: newEntity }
        newTarget[dbConn][`migrate`] = false
    }
    else {
        target[`new_entity_${Object.keys(target).length}`] = newEntity
    }
    return data
}

export const dataAccess = (yamlData, coreLibName) => {
    const dbConns = Object.keys(yamlData[coreLibName]['config']['data'])
    const newDataAccess = {
        entity: "details",
        db_connection: dbConns[0],
        is_crud: true,
        is_crud_soft_delete: true,
        is_crud_soft_delete_token: true,
    }
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = [coreLibName, 'data_layers', 'data_access']
    const target = getValueAtPath(data, steps)
    target['NewDataAccess' + (Object.keys(target).length + 1)] = newDataAccess
    return data
}

export const dbConnection = (yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = [coreLibName, 'config', 'data']
    const target = getValueAtPath(data, steps)
    const dbConnName = `newdb${(Object.keys(target).length + 1)}`
    const envSteps = [coreLibName, 'env']
    const envTarget = getValueAtPath(data, envSteps)

    const newDbConn = {
        log_queries: false,
        create_db: true,
        session: {
            pool_recycle: 3200,
            pool_pre_ping: false,
        },
        url: {
            protocol: "postgresql",
            username: "${oc.env:"+dbConnName.toUpperCase()+"_USER}",
            password: "${oc.env:"+dbConnName.toUpperCase()+"_PASSWORD}",
            host: "${oc.env:"+dbConnName.toUpperCase()+"_HOST}",
            port: "${oc.env:"+dbConnName.toUpperCase()+"_PORT}",
            file: "${oc.env:"+dbConnName.toUpperCase()+"_DB}",
        },
    }

    envTarget[`${dbConnName.toUpperCase()}_USER`] = 'user'
    envTarget[`${dbConnName.toUpperCase()}_PASSWORD`] = 'password'
    envTarget[`${dbConnName.toUpperCase()}_HOST`] = 'localhost'
    envTarget[`${dbConnName.toUpperCase()}_PORT`] = 5432
    envTarget[`${dbConnName.toUpperCase()}_DB`] = dbConnName
    target[dbConnName] = newDbConn

    return data
}

export const cache = (yamlData, coreLibName) => {
    const newCache = {
        type: "memcached",
        url: {
            host: "${oc.env:MEMCACHED_HOST}",
            port: "${oc.env:MEMCACHED_PORT}",
        },
    }
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = [coreLibName, 'config', 'cache']
    const target = getValueAtPath(data, steps)
    target[`new_cache_${(Object.keys(target).length + 1)}`] = newCache

    const envSteps = [coreLibName, 'env']
    const envTarget = getValueAtPath(data, envSteps)
    envTarget['MEMCACHED_HOST'] = 'localhost'
    envTarget['MEMCACHED_PORT'] = 11211

    return data

}

export const job = (yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = [coreLibName, 'config', 'jobs']
    const target = getValueAtPath(data, steps)
    const newName = `new_job_${(Object.keys(target).length + 1)}`
    const snakeCoreLib = toSnakeCase(coreLibName)
    const newJob = {
        initial_delay: "0s",
        frequency: "",
        handler: {
            _target_:
                `${snakeCoreLib}.${snakeCoreLib}.jobs.${newName}.${toCamelCase(newName)}`,
        },
    }
    target[`new_job_${(Object.keys(target).length + 1)}`] = newJob
    return data
}