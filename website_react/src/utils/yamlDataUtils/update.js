export const updateEnv = (path, value, yamlData) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const target = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
    target[steps.at(-1)] = value;
    return data
}

export const updateCache = (path, value, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const target = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
    if(path.includes('type')){
        if(target.type === 'memory'){
            delete target['url']
        }
        if(target.type === 'memcached'){
            if(target.hasOwnProperty('url')){
                delete target['url']['protocol']
            }
            else{
                target['url'] = {}
            }

            if(!target['url'].hasOwnProperty('host')){
                target['url']['host'] = '${oc.env:MEMCACHED_HOST}'
                data[coreLibName]['env']['MEMCACHED_HOST'] = 'localhost'
            }
            if(!target['url'].hasOwnProperty('port')){
                target['url']['port'] = '${oc.env:MEMCACHED_PORT}'
                data[coreLibName]['env']['MEMCACHED_PORT'] = 11211
            }
        }
        if(target.type === 'redis'){
            if(target.hasOwnProperty('url')){
                delete target['url']['protocol']
            }
            else{
                target['url'] = {}
            }

            if(!target['url'].hasOwnProperty('host')){
                target['url']['host'] = '${oc.env:REDIS_HOST}'
                data[coreLibName]['env']['REDIS_HOST'] = 'localhost'
            }
            if(!target['url'].hasOwnProperty('port')){
                target['url']['port'] = '${oc.env:REDIS_PORT}'
                data[coreLibName]['env']['REDIS_PORT'] = 6379
            }
            if(!target['url'].hasOwnProperty('protocol')){
                target['url']['protocol'] = 'redis'
            }
        }
    }
    return data
}

export const updateDBConn = (path, value, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const steps = path.split(".")
    const dbConn = steps.at(-3)
    const target = steps.slice(0, -2).reduce((key, val) => key && key[val] ? key[val] : '', data);
    if(value.toLowerCase() === 'mongodb'){
        target['url']['protocol'] = value.toLowerCase()
        delete target['create_db']
        delete target['log_queries']
        delete target['session']
    }
    else if(value.toLowerCase() === 'sqlite'){
        target['url']['protocol'] = value.toLowerCase()
        if(!target.hasOwnProperty('create_db')){
            target['create_db'] = true
        }
        if(!target.hasOwnProperty('log_queries')){
            target['log_queries'] = false
        }
        if(!target.hasOwnProperty('session')){
            console.log('ad')
            const session = {
                pool_recycle: 3200,
                pool_pre_ping: false
            }
            target['session'] = session
        }
        delete target['url']['username']
        delete data[coreLibName]['env'][dbConn.toUpperCase() +'_USER']
        delete target['url']['password']
        delete data[coreLibName]['env'][dbConn.toUpperCase() +'_PASSWORD']
        delete target['url']['host']
        delete data[coreLibName]['env'][dbConn.toUpperCase() +'_HOST']
        delete target['url']['port']
        delete data[coreLibName]['env'][dbConn.toUpperCase() +'_PORT']
        delete target['url']['file']
        delete data[coreLibName]['env'][dbConn.toUpperCase() +'_DB']
    }
    else{
        target['url']['protocol'] = value.toLowerCase()
        if(!target.hasOwnProperty('create_db')){
            target['create_db'] = true
        }
        if(!target.hasOwnProperty('log_queries')){
            target['log_queries'] = false
        }
        if(!target.hasOwnProperty('session')){
            const session = {
                pool_recycle: 3200,
                pool_pre_ping: false
            }
            target['session'] = session
        }
        if(!target['url'].hasOwnProperty('username')){
            target['url']['username'] = '${oc.env:'+ dbConn.toUpperCase() +'_USER}'
            data[coreLibName]['env'][dbConn.toUpperCase() +'_USER'] = 'username'
        }
        if(!target['url'].hasOwnProperty('password')){
            target['url']['password'] = '${oc.env:'+ dbConn.toUpperCase() +'_PASSWORD}'
            data[coreLibName]['env'][dbConn.toUpperCase() +'_PASSWORD'] = ''
        }
        if(!target['url'].hasOwnProperty('host')){
            target['url']['host'] = '${oc.env:'+ dbConn.toUpperCase() +'_HOST}'
            data[coreLibName]['env'][dbConn.toUpperCase() +'_HOST'] = 'localhost'
        }
        if(!target['url'].hasOwnProperty('port')){
            target['url']['port'] = '${oc.env:'+ dbConn.toUpperCase() +'_PORT}'
            data[coreLibName]['env'][dbConn.toUpperCase() +'_PORT'] = 1234
        }
        if(!target['url'].hasOwnProperty('file')){
            target['url']['file'] = '${oc.env:'+ dbConn.toUpperCase() +'_DB}'
            data[coreLibName]['env'][dbConn.toUpperCase() +'_DB'] = dbConn
        }
    }
    return data
}

export const updateMongoEntities = (path, value, yamlData, coreLibName) => {
    const data = JSON.parse(JSON.stringify(yamlData))
    const pathSplit = path.split(".")
    const dbConn = pathSplit.at(pathSplit.indexOf('data') + 1)
    const entitySteps = [coreLibName, 'data_layers', 'data', dbConn]
    const target = entitySteps.reduce((key, val) => key && key[val] ? key[val] : '', data);
    Object.keys(target).forEach(entity => {
        if (entity !== 'migrate') {
            delete target[entity]['columns']
            delete target[entity]['is_soft_delete']
            delete target[entity]['is_soft_delete_token']
        }
    })

    return data
}