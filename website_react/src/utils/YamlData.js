import { isObject, getValueAtPath } from "./commonUtils"
import {rename} from './yamlDataUtils/rename'
import * as update from './yamlDataUtils/update'
import * as create from './yamlDataUtils/create'
export class YamlData {

    init(data) {
        this.yaml = data
        this.coreLibName = data.core_lib.name
    }

    set(path, value, isEnv, addOrRemove) {
        let data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        if (path === 'core_lib.name') {
            data.core_lib.name = value
            this.yaml = data
            this.coreLibName = value
        }
        else {
            const objField = getValueAtPath(data, steps)
            const fieldName = steps[steps.length - 1]
            if (isObject(objField)) {
                const oldKeyName = steps[steps.length - 1]
                const parent = getValueAtPath(data, steps.slice(0, -1))
                parent[value] = parent[oldKeyName];
                delete parent[oldKeyName]
                this.yaml = data
                steps[steps.length - 1] = value
                return steps.join('.')
            } else {
                if (isEnv) {
                    this.yaml = update.updateEnv(isEnv, value, this.yaml)
                    return path
                }
                if(path.includes('setup.classifiers')){
                    this.yaml = update.updateSetup(path, value, this.yaml, addOrRemove)
                    return path
                }
                if(path.includes('core_lib.entities') && path.endsWith('nullable')){
                    this.yaml = update.updateNullable(path, this.yaml, addOrRemove)
                    return path
                }
                if(path.includes('columns') && path.endsWith('default')){
                    this.yaml = update.updateColumnDefault(path, value, this.yaml)
                    return path
                }
                const parent = getValueAtPath(data, steps.slice(0, -1));
                parent[fieldName] = value;
                data = rename(path, value, data, this.yaml)
                this.yaml = data
                if (path.includes('url.protocol') && path.includes('core_lib.connections')) {
                    this.yaml = update.updateDBConn(path, value, this.yaml, this.coreLibName)
                }
                if (path.includes('core_lib.caches')){
                    this.yaml = update.updateCache(path, value, this.yaml, this.coreLibName)
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

    createColumn(path) {
        this.yaml = create.columns(path, this.yaml, this.coreLibName)
    }

    delete(path) {
        const data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        const parent = getValueAtPath(data, steps.slice(0, -1));
        parent.splice(steps.at(-1), 1);
        this.yaml = data
    }

    get(path) {
        return path.split('.').reduce((obj, key) => {
            return obj && obj[key];
        }, this.yaml);
    }

    listChildrenUnderPath(path) {
        const res = []
        const list = this.get(path) 
        if (path === 'core_lib.entities') {
            const entityRes = []
            list.forEach((entity, index) => {
                entityRes.push({ name: entity.key, path: path + '.' + index, dbConnection: entity.db_connection })
            })
            return entityRes
        }
        if (path === 'core_lib.connections') {
            list.forEach((dbConn, index) => {
                res.push({ name: dbConn.key, path: path + '.' + index, hasEntity: true })
            })
            return res

        }
        if(list instanceof Array){
            list.forEach((item, index )=> {
                res.push({ name: item.key, path: path + '.' + index })
            })
        }
        return res
    }

    toJSON() {
        return this.yaml
    }
}