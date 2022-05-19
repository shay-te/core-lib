import { toCamelCase, toSnakeCase, getValueAtPath } from "../commonUtils"

export const entity = (dbConn, yamlData, coreLibName) => {
    const newNormalEntity = {
        db_connection: dbConn,
        columns: [
            {
                key: 'column_name',
                type: "VARCHAR",
                default: null,
            },
        ],
        is_soft_delete: true,
        is_soft_delete_token: true,
    }

    const newMongoEntity = {
        db_connection: dbConn,
    }

    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'entities']
    const target = getValueAtPath(data, steps)
    const dbConnSteps = ['core_lib', 'connections']
    const dbConns = getValueAtPath(data, dbConnSteps)
    let newEntity = {key: `new_entity_${target.length}`}
    dbConns.forEach(connection => {
        if(connection.key === dbConn && connection['url']['protocol'] === 'mongodb'){
            newEntity = Object.assign(newEntity, newMongoEntity)
        }else{
            newEntity = Object.assign(newEntity, newNormalEntity)
        }
    })
    target.push(newEntity)
    return data
}

export const dataAccess = (yamlData, coreLibName) => {
    const dbConn = yamlData.core_lib.connections[0].key
   
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'data_accesses']
    const target = getValueAtPath(data, steps)
    const newDataAccess = {
        key: 'NewDataAccess' + (target.length + 1),
        entity: "details",
        db_connection: dbConn,
        is_crud: true,
        is_crud_soft_delete: true,
        is_crud_soft_delete_token: true,
    }
    target.push(newDataAccess)
    return data
}

export const dbConnection = (yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'connections']
    const target = getValueAtPath(data, steps)
    const dbConnName = `newdb${target.length + 1}`
    const envSteps = ['core_lib', 'env']
    const envTarget = getValueAtPath(data, envSteps)

    const newDbConn = {
        key: dbConnName,
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
    target.push(newDbConn)

    return data
}

export const cache = (yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'caches']
    const target = getValueAtPath(data, steps)
    const newCacheName = `new_cache_${target.length + 1}`
    const newCache = {
        key: newCacheName,
        type: "memcached",
        url: {
            host: "${oc.env:" + newCacheName.toUpperCase() + "_HOST}",
            port: "${oc.env:" + newCacheName.toUpperCase() + "_PORT}",
        },
    }
    target.push(newCache)

    const envSteps = ['core_lib', 'env']
    const envTarget = getValueAtPath(data, envSteps)
    envTarget[`${newCacheName.toUpperCase()}_HOST`] = 'localhost'
    envTarget[`${newCacheName.toUpperCase()}_PORT`] = 11211

    return data

}

export const job = (yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'jobs']
    const target = getValueAtPath(data, steps)
    const newName = `new_job_${target.length + 1}`
    const snakeCoreLib = toSnakeCase(coreLibName)
    const newJob = {
        key: newName,
        initial_delay: "0s",
        frequency: "",
        handler: {
            _target_:
                `${snakeCoreLib}.${snakeCoreLib}.jobs.${newName}.${toCamelCase(newName)}`,
        },
    }
    target.push(newJob)
    return data
}

export const columns = (path, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split('.')
    const target = getValueAtPath(data, steps)
    const newColumn = {
        key: `column_${target.length + 1}`,
        type: 'VARCHAR',
        default: '',
    }
    target.push(newColumn)
    return data
}