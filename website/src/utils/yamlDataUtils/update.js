import { getValueAtPath } from "../commonUtils"

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
        }
        if (target.type === 'memcached') {
            if (target.hasOwnProperty('url')) {
                delete target['url']['protocol']
            }
            else {
                target['url'] = {}
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

export const updateDBConn = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const target = getValueAtPath(data, steps.slice(0, -2))
    const dbConn = target.key
    if (value.toLowerCase() === 'mongodb') {
        target['url']['protocol'] = value.toLowerCase()
        delete target['create_db']
        delete target['log_queries']
        delete target['session']
    }
    else if (value.toLowerCase() === 'sqlite') {
        target['url']['protocol'] = value.toLowerCase()
        if (!target.hasOwnProperty('create_db')) {
            target['create_db'] = true
        }
        if (!target.hasOwnProperty('log_queries')) {
            target['log_queries'] = false
        }
        if (!target.hasOwnProperty('session')) {
            const session = {
                pool_recycle: 3200,
                pool_pre_ping: false
            }
            target['session'] = session
        }
        delete target['url']['username']
        delete data.core_lib.env[dbConn.toUpperCase() + '_USER']
        delete target['url']['password']
        delete data.core_lib.env[dbConn.toUpperCase() + '_PASSWORD']
        delete target['url']['host']
        delete data.core_lib.env[dbConn.toUpperCase() + '_HOST']
        delete target['url']['port']
        delete data.core_lib.env[dbConn.toUpperCase() + '_PORT']
        delete target['url']['file']
        delete data.core_lib.env[dbConn.toUpperCase() + '_DB']
    }
    else {
        target['url']['protocol'] = value.toLowerCase()
        if (!target.hasOwnProperty('create_db')) {
            target['create_db'] = true
        }
        if (!target.hasOwnProperty('log_queries')) {
            target['log_queries'] = false
        }
        if (!target.hasOwnProperty('session')) {
            const session = {
                pool_recycle: 3200,
                pool_pre_ping: false
            }
            target['session'] = session
        }
        if (!target['url'].hasOwnProperty('username')) {
            target['url']['username'] = '${oc.env:' + dbConn.toUpperCase() + '_USER}'
            data.core_lib.env[dbConn.toUpperCase() + '_USER'] = 'username'
        }
        if (!target['url'].hasOwnProperty('password')) {
            target['url']['password'] = '${oc.env:' + dbConn.toUpperCase() + '_PASSWORD}'
            data.core_lib.env[dbConn.toUpperCase() + '_PASSWORD'] = ''
        }
        if (!target['url'].hasOwnProperty('host')) {
            target['url']['host'] = '${oc.env:' + dbConn.toUpperCase() + '_HOST}'
            data.core_lib.env[dbConn.toUpperCase() + '_HOST'] = 'localhost'
        }
        if (!target['url'].hasOwnProperty('port')) {
            target['url']['port'] = '${oc.env:' + dbConn.toUpperCase() + '_PORT}'
            data.core_lib.env[dbConn.toUpperCase() + '_PORT'] = 1234
        }
        if (!target['url'].hasOwnProperty('file')) {
            target['url']['file'] = '${oc.env:' + dbConn.toUpperCase() + '_DB}'
            data.core_lib.env[dbConn.toUpperCase() + '_DB'] = dbConn
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
    }
    return data
}

export const updateFunctionsCheckbox = (path, yamlData, addOrRemove) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const target = getValueAtPath(data, pathSplit.slice(0, -1))
    if(path.includes('cache_invalidate') && !target.hasOwnProperty('cache_key')){
        return data
    }
    target[pathSplit.at(-1)] = addOrRemove
    return data
}

export const updateFunctionsCache = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".") 
    const target = getValueAtPath(data, pathSplit.slice(0, -1))
    if(!value){
        delete target['cache_key']
        delete target['cache_invalidate']
    }
    else{
        target.cache_key = value
        if(!target.hasOwnProperty('cache_invalidate')){
            target.cache_invalidate = false
        }
    }
    return data
}
