import { toCamelCase, toSnakeCase, getValueAtPath, setValueAtPath } from "../commonUtils"
export const rename = (path, value, yamlData, oldYamlData) => {
    const pathSplit = path.split('.')
    const index = pathSplit.at(-2)
    if (path.includes('connections') && path.includes('key')) {
        return renameConnEvents(pathSplit, oldYamlData.core_lib.connections[index], value, yamlData);
    }
    if (path.includes('entities') && path.includes('key') && !path.includes('columns')) {
        return renameEntityEvents(oldYamlData.core_lib.entities[index], value, yamlData);
    }
    if (path.includes('jobs') && path.includes('key')) {
        return renameJobEvents(pathSplit, value, yamlData);
    }
    if (path.includes('caches') && path.includes('key')) {
        return renameCacheEvents(pathSplit, oldYamlData.core_lib.caches[index], value, yamlData);
    }
    if (path.includes('data_accesses') && path.includes('key') && !path.includes('functions')) {
        return renameDataAccessEvents(oldYamlData.core_lib.data_accesses[index], value, yamlData);
    }
    return yamlData
}

const renameCacheEvents = (path, oldValue, newValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'caches', path.at(-2)]
    const target = getValueAtPath(data, steps)
    const envSteps = ['core_lib', 'env']
    const envTarget = getValueAtPath(data, envSteps)
    if(target.type !== 'memory'){
        envTarget[`${newValue.toUpperCase()}_PORT`] = envTarget[`${oldValue.key.toUpperCase()}_PORT`]
        envTarget[`${newValue.toUpperCase()}_HOST`] = envTarget[`${oldValue.key.toUpperCase()}_HOST`]
        delete envTarget[`${oldValue.key.toUpperCase()}_PORT`]
        delete envTarget[`${oldValue.key.toUpperCase()}_HOST`]
    }
    return data
}

const renameJobEvents = (path, newValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = ['core_lib', 'jobs', path.at(-2)]
    const coreLibName = yamlData.core_lib.name
    const target = getValueAtPath(data, steps)
    const snakeCoreLib = toSnakeCase(coreLibName)
    target['handler']['_target_'] = `${snakeCoreLib}.${snakeCoreLib}.jobs.${newValue}.${toCamelCase(newValue)}`
    return data
}

const renameEntityEvents = (oldValue, newValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    // Data access
    const daSteps = ['core_lib', 'data_accesses']
    const daTarget = getValueAtPath(data, daSteps)
    if(daTarget){
        daTarget.forEach(dataAccess => {
            if (dataAccess.entity === oldValue.key && dataAccess.connection === oldValue.connection) {
                dataAccess['entity'] = newValue
            }
        })
    }
    return data
}

const renameDataAccessEvents = (oldValue, newValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const serviceSteps = ['core_lib', 'services']
    const serviceTarget = getValueAtPath(data, serviceSteps)
    if(serviceTarget){
        serviceTarget.forEach(service => {
            if (service.data_access === oldValue.key) {
                service['data_access'] = newValue
            }
        })
    }
    return data
}

const renameConnEvents = (path, oldValue, newValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    // Environment varibales
    const envSteps = ['core_lib', 'env']
    const envTarget = getValueAtPath(data, envSteps)
    if(!envTarget){
        setValueAtPath(data, envSteps, {})
        envTarget = getValueAtPath(data, envSteps)
    }
    const newHost = `${newValue.toUpperCase()}_HOST`
    const newPort = `${newValue.toUpperCase()}_PORT`
    const newPassword = `${newValue.toUpperCase()}_PASSWORD`
    const newUser = `${newValue.toUpperCase()}_USER`
    const newDB = `${newValue.toUpperCase()}_DB`
    envTarget[newHost] = envTarget[`${oldValue.key.toUpperCase()}_HOST`];
    envTarget[newPort] = envTarget[`${oldValue.key.toUpperCase()}_PORT`];
    envTarget[newPassword] = envTarget[`${oldValue.key.toUpperCase()}_PASSWORD`];
    envTarget[newUser] = envTarget[`${oldValue.key.toUpperCase()}_USER`];
    envTarget[newDB] = envTarget[`${oldValue.key.toUpperCase()}_DB`];
    envTarget[newDB] = newValue
    delete envTarget[`${oldValue.key.toUpperCase()}_HOST`]
    delete envTarget[`${oldValue.key.toUpperCase()}_PORT`]
    delete envTarget[`${oldValue.key.toUpperCase()}_PASSWORD`]
    delete envTarget[`${oldValue.key.toUpperCase()}_USER`]
    delete envTarget[`${oldValue.key.toUpperCase()}_DB`]
    // Connection
    const connSteps = ['core_lib', 'connections', path.at(-2)]
    const connTarget = getValueAtPath(data, connSteps)
    if(connTarget.config.url.protocol !== 'sqlite'){
        if(!connTarget.type.includes('Neo4jConnectionRegistry') && !connTarget.type.includes('SolrConnectionRegistry')){
            connTarget['config']['url']['password'] = '${oc.env:' + newPassword + '}'
            connTarget['config']['url']['username'] = '${oc.env:' + newUser + '}'
        }
        if(!connTarget.type.includes('Neo4jConnectionRegistry')){
            connTarget['config']['url']['file'] = '${oc.env:' + newDB + '}'
        }
        connTarget['config']['url']['host'] = '${oc.env:' + newHost + '}'
        connTarget['config']['url']['port'] = '${oc.env:' + newPort + '}'
    }
    // Entity group
    const entitySteps = ['core_lib', 'entities']
    const entityTarget = getValueAtPath(data, entitySteps)
    entityTarget.forEach(entity => {
        if (entity.connection === oldValue.key) {
            entity.connection = newValue
        }
    })

    // Data access
    const daSteps = ['core_lib', 'data_accesses']
    const daTarget = getValueAtPath(data, daSteps)
    daTarget.forEach(dataAccess => {
        if (dataAccess.connection === oldValue.key) {
            dataAccess.connection = newValue
        }
    })
    return data
}