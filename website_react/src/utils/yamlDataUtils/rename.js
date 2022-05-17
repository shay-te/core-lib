import { toCamelCase, toSnakeCase, getValueAtPath } from "../commonUtils"
export const rename = (path, value, yamlData, oldYamlData) => {
    const pathSplit = path.split('.')
    if (path.includes('connections') && path.includes('key')) {
        return renameDBConnEvents(pathSplit, oldYamlData.core_lib.connections[pathSplit.at(-2)], value, yamlData);
    }
    if (path.includes('entities') && path.includes('key')) {
        return renameEntityEvents(oldYamlData.core_lib.entities[pathSplit.at(-2)], value, yamlData);
    }
    if (path.includes('jobs') && path.includes('key')) {
        return renameJobEvents(pathSplit, value, yamlData);
    }
    return yamlData
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
    daTarget.forEach(dataAccess => {
        if (dataAccess.entity === oldValue.key && dataAccess.db_connection === oldValue.db_connection) {
            dataAccess['entity'] = newValue
        }
    })
    return data
}

const renameDBConnEvents = (path, oldValue, newValue, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const coreLibName = yamlData.core_lib.name
    // Environment varibales
    const envSteps = ['core_lib', 'env']
    const envTarget = getValueAtPath(data, envSteps)
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
    // DB Connection
    const connSteps = ['core_lib', 'connections', path.at(-2)]
    const connTarget = getValueAtPath(data, connSteps)
    connTarget['host'] = '${oc.env:' + newHost + '}'
    connTarget['port'] = '${oc.env:' + newPort + '}'
    connTarget['password'] = '${oc.env:' + newPassword + '}'
    connTarget['username'] = '${oc.env:' + newUser + '}'
    connTarget['file'] = '${oc.env:' + newDB + '}'
    // Entity group
    const entitySteps = ['core_lib', 'entities']
    const entityTarget = getValueAtPath(data, entitySteps)
    entityTarget.forEach(entity => {
        if (entity.db_connection === oldValue.key) {
            entity.db_connection = newValue
        }
    })

    // Data access
    const daSteps = ['core_lib', 'data_accesses']
    const daTarget = getValueAtPath(data, daSteps)
    daTarget.forEach(dataAccess => {
        if (dataAccess.db_connection === oldValue.key) {
            dataAccess.db_connection = newValue
        }
    })
    return data
}