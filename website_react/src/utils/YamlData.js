import { isObject } from "./commonUtils"
import {rename} from './yamlDataUtils/rename'
import * as update from './yamlDataUtils/update'
import * as create from './yamlDataUtils/create'
export class YamlData {

    init(data) {
        this.yaml = data
        this.coreLibName = Object.keys(data)[0]
    }

    set(path, value, isEnv) {
        const data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        if (steps.length === 1) {
            data[value] = data[this.coreLibName]
            delete data[this.coreLibName]
            this.yaml = data
            this.coreLibName = value
        }
        else {
            const objField = steps.reduce((key, val) => key && key[val] ? key[val] : '', data);
            const fieldName = steps[steps.length - 1]
            if (isObject(objField)) {
                const oldKeyName = steps[steps.length - 1]
                const parent = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
                parent[value] = parent[oldKeyName];
                delete parent[oldKeyName]
                this.yaml = data
                steps[steps.length - 1] = value
                if (path.includes('config.data') && steps.length === 4) {
                    this.yaml = rename(path, value, this.yaml, this.coreLibName)
                }
                if (path.includes('data_layers.data') && steps.length === 5) {
                    this.yaml = rename(path, value, this.yaml, this.coreLibName)
                }
                if (path.includes('jobs') && steps.length === 4){
                    this.yaml = rename(path, value, this.yaml, this.coreLibName)
                }
                return steps.join('.')
            } else {
                if (isEnv) {
                    this.yaml = update.updateEnv(isEnv, value, this.yaml)
                    return path
                }
                const parent = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
                parent[fieldName] = value;
                this.yaml = data
                if (path.includes('url.protocol') && path.includes('config.data')) {
                    if(value.toLowerCase() === 'mongodb'){
                        this.yaml = update.updateMongoEntities(path, value, this.yaml)
                    }
                    this.yaml = update.updateDBConn(path, value, this.yaml)
                }
                if (path.includes('cache')){
                    this.yaml = update.updateCache(path, value, this.yaml)
                }
                return steps.join('.')
            }
        }
        return path
    }

    createEntity(dbConn) {
        this.yaml = create.entity(dbConn, this.yaml, this.coreLibName)
    }

    createDataAccess() {
        this.yaml = create.dataAccess(this.yaml, this.coreLibName)
    }

    createDBConnection() {
        this.yaml = create.dbConnection(this.yaml, this.coreLibName)
    }

    createCache() {
        this.yaml = create.cache(this.yaml, this.coreLibName)
    }

    createJob() {
        this.yaml = create.job(this.yaml, this.coreLibName)
    }

    delete(path) {
        const data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        const oldKeyName = steps[steps.length - 1]
        const parent = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
        delete parent[oldKeyName]
        this.yaml = data
    }

    get(path) {
        return path.split('.').reduce((obj, key) => {
            return obj && obj[key];
        }, this.yaml);
    }

    listChildrenUnderPath(path) {
        const res = []
        const newPath = this.coreLibName + '.' + path
        const list = this.get(newPath)
        if (path === 'data_layers.data') {
            const entityRes = []
            Object.keys(list).forEach((dbConn, index) => {
                const entityDbconnPath = newPath + '.' + dbConn
                const entityList = this.get(entityDbconnPath)
                entityRes.push({ [dbConn]: [] })
                Object.keys(entityList).forEach(entity => {
                    if (entity !== 'migrate') {
                        entityRes[index][dbConn].push({ name: entity, path: entityDbconnPath + '.' + entity, dbConnection: dbConn })
                    }
                })
            })
            return entityRes
        }
        if (path === 'config.data') {
            Object.keys(list).forEach(dbConn => {
                if (list[dbConn]['url']['protocol'] === 'mongodb')
                    res.push({ name: dbConn, path: newPath + '.' + dbConn, hasEntity: false })
                else
                    res.push({ name: dbConn, path: newPath + '.' + dbConn, hasEntity: true })
            })
            return res

        }
        Object.keys(list).forEach(item => {
            res.push({ name: item, path: newPath + '.' + item })
        })
        return res
    }

    toJSON() {
        return this.yaml
    }
}