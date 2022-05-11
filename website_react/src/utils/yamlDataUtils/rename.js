import { toCamelCase, toSnakeCase } from "../commonUtils"
export const rename = (path, value, yamlData, coreLibName) => {
    const pathSplit = path.split('.')
    if (path.includes('config.data')) {
        return renameDBConnEvents(pathSplit.at(-1), value, yamlData, coreLibName);
    }
    if (path.includes('data_layers.data')) {
        return renameEntityEvents(pathSplit.at(-1), value, yamlData, coreLibName);
    }
    if (path.includes('config.jobs')) {
        return renameJobEvents(pathSplit.at(-1), value, yamlData, coreLibName);
    }
}

const renameJobEvents = (oldValue, newValue, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = [coreLibName, 'config', 'jobs', newValue]
    const target = steps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    const snakeCoreLib = toSnakeCase(coreLibName)
    target['handler']['_target_'] = `${snakeCoreLib}.${snakeCoreLib}.jobs.${newValue}.${toCamelCase(newValue)}`
    return data
}

const renameEntityEvents = (oldValue, newValue, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    // Data access
    const daSteps = [coreLibName, 'data_layers', 'data_access']
    const daTarget = daSteps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    Object.keys(daTarget).forEach(dataAccess => {
        if (daTarget[dataAccess]['entity'] === oldValue) {
            daTarget[dataAccess]['entity'] = newValue
        }
    })
    return data
}

const renameDBConnEvents = (oldValue, newValue, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    // Environment varibales
    const envSteps = [coreLibName, 'env']
    const envTarget = envSteps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    const newHost = `${newValue.toUpperCase()}_HOST`
    const newPort = `${newValue.toUpperCase()}_PORT`
    const newPassword = `${newValue.toUpperCase()}_PASSWORD`
    const newUser = `${newValue.toUpperCase()}_USER`
    const newDB = `${newValue.toUpperCase()}_DB`
    envTarget[newHost] = envTarget[`${oldValue.toUpperCase()}_HOST`];
    envTarget[newPort] = envTarget[`${oldValue.toUpperCase()}_PORT`];
    envTarget[newPassword] = envTarget[`${oldValue.toUpperCase()}_PASSWORD`];
    envTarget[newUser] = envTarget[`${oldValue.toUpperCase()}_USER`];
    envTarget[newDB] = envTarget[`${oldValue.toUpperCase()}_DB`];
    envTarget[newDB] = newValue
    delete envTarget[`${oldValue.toUpperCase()}_HOST`]
    delete envTarget[`${oldValue.toUpperCase()}_PORT`]
    delete envTarget[`${oldValue.toUpperCase()}_PASSWORD`]
    delete envTarget[`${oldValue.toUpperCase()}_USER`]
    delete envTarget[`${oldValue.toUpperCase()}_DB`]
    // DB Connection
    const connSteps = [coreLibName, 'config', 'data', newValue, 'url']
    const connTarget = connSteps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    connTarget['host'] = '${oc.env:' + newHost + '}'
    connTarget['port'] = '${oc.env:' + newPort + '}'
    connTarget['password'] = '${oc.env:' + newPassword + '}'
    connTarget['username'] = '${oc.env:' + newUser + '}'
    connTarget['file'] = '${oc.env:' + newDB + '}'
    // Entity group
    const entitySteps = [coreLibName, 'data_layers', 'data']
    const entityTarget = entitySteps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    if (entityTarget.hasOwnProperty(oldValue)) {
        entityTarget[newValue] = entityTarget[oldValue]
        delete entityTarget[oldValue]
        console.log(data)
        Object.keys(entityTarget[newValue]).forEach(entity => {
            if (entity !== 'migrate') {
                entityTarget[newValue][entity]['db_connection'] = newValue
            }
        })
    }

    // Data access
    const daSteps = [coreLibName, 'data_layers', 'data_access']
    const daTarget = daSteps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    Object.keys(daTarget).forEach(dataAccess => {
        if (daTarget[dataAccess]['db_connection'] === oldValue) {
            daTarget[dataAccess]['db_connection'] = newValue
        }
    })
    return data
}