import { getValueAtPath } from "../commonUtils";

export const deleteData = (path, delData, yamData) => {
    let data = JSON.parse(JSON.stringify(yamData))
    if(path.includes('connections')){
        if(confirm('Deleting this connection will delete the enitites attached to this connection.') === true){
            data = deleteConnData(delData, data)
        }
    } else if (path.includes('caches')){
        data = deleteEnv(delData, data)
    } else if (path.includes('data_accesses')){
        data = deleteDataAccessData(delData, data)
    }
    return data
}

const deleteConnData = (connData, yamData) => {
    const data = JSON.parse(JSON.stringify(yamData))
    const entitySteps = ['core_lib', 'entities']
    let entityTarget = getValueAtPath(data, entitySteps);
    const connName = connData[0].key
    const entities = []
    if(entityTarget.length > 0){
        entityTarget.forEach((entity) => {
            if(entity.connection !== connName){
                entities.push(entity)
            }
        });
        data.core_lib.entities = entities
        entityTarget = entities.slice(0)
    }
    const dataAccessSteps = ['core_lib', 'data_accesses']
    const daTarget = getValueAtPath(data, dataAccessSteps)
    if(daTarget.length > 0) {
        daTarget.forEach((dataAccess, index) => {
            if(dataAccess.connection === connName){
                delete daTarget[index]['connection']
            }
        })
    }
    return deleteEnv(connData, data)
}

const deleteDataAccessData = (daData, yamData) => {
    const data = JSON.parse(JSON.stringify(yamData))
    const daName = daData[0].key
    const serviceSteps = ['core_lib', 'services']
    const serviceTarget = getValueAtPath(data, serviceSteps)
    if(serviceTarget.length > 0) {
        serviceTarget.forEach((service, index) => {
            if(service.data_access === daName){
                delete serviceTarget[index]['data_access']
            }
        })
    }
    return data
}

const deleteEnv = (delData, yamData) => {
    const data = JSON.parse(JSON.stringify(yamData))
    const delName = delData[0].key
    delete data.core_lib.env[delName.toUpperCase() + '_USER']
    delete data.core_lib.env[delName.toUpperCase() + '_PASSWORD']
    delete data.core_lib.env[delName.toUpperCase() + '_HOST']
    delete data.core_lib.env[delName.toUpperCase() + '_PORT']
    delete data.core_lib.env[delName.toUpperCase() + '_DB']
    return data
} 

