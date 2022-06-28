import { isObject, getValueAtPath } from "./commonUtils"
import {rename} from './yamlDataUtils/rename'
import * as update from './yamlDataUtils/update'
import * as create from './yamlDataUtils/create'
import {deleteData} from './yamlDataUtils/delete'
export class YamlData {

    init(data) {
        this.yaml = data
        this.coreLibName = data.core_lib.name
    }

    set(path, value, isEnv, addOrRemove, isBool) {
        let data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        if (path === 'core_lib.name') {
            data.core_lib.name = value
            this.yaml = data
            this.coreLibName = value
        }
        else {
            if(isBool){
                value = value.toLowerCase() === 'true'
            }
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
                if(path.includes('functions') && (path.endsWith('result_to_dict') || path.endsWith('cache_invalidate'))){
                    this.yaml = update.updateFunctionsCheckbox(path, this.yaml, addOrRemove)
                    return path
                }
                if(path.includes('functions') && path.endsWith('cache_key')){
                    this.yaml = update.updateFunctionsCache(path, value, this.yaml)
                    return path
                }
                const parent = getValueAtPath(data, steps.slice(0, -1));
                parent[fieldName] = value;
                data = rename(path, value, data, this.yaml)
                this.yaml = data
                if (path.includes('url.protocol') && path.includes('core_lib.connections')) {
                    this.yaml = update.updateConn(path, value, this.yaml)
                }
                if (path.includes('core_lib.caches')){
                    this.yaml = update.updateCache(path, this.yaml)
                }
                if (path.includes('core_lib.data_accesses')){
                    this.yaml = update.updateDataAccess(path, value, this.yaml)
                }
                if (path.includes('core_lib.services')){
                    this.yaml = update.updateService(path, value, this.yaml)
                }
                return steps.join('.')
            }
        }
        return path
    }

    createEntity() {
        this.yaml = create.entity(this.yaml)
    }

    createDataAccess() {
        this.yaml = create.dataAccess(this.yaml)
    }

    createConnection() {
        this.yaml = create.connection(this.yaml)
    }

    createCache() {
        this.yaml = create.cache(this.yaml)
    }

    createJob() {
        this.yaml = create.job(this.yaml, this.coreLibName)
    }

    createColumn(path) {
        this.yaml = create.columns(path, this.yaml)
    }

    createFunction(path) {
        this.yaml = create.functions(path, this.yaml)
    }

    createServices(path){
        this.yaml = create.services(this.yaml)
    }

    delete(path) {
        let data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        const parent = getValueAtPath(data, steps.slice(0, -1));
        const delData = parent.splice(steps.at(-1), 1);
        data = deleteData(path, delData, data)
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
        if(!list){
            return res
        }
        if (path === 'core_lib.entities') {
            const entityRes = []
            list.forEach((entity, index) => {
                entityRes.push({ name: `${entity.key} (${entity.connection})`, path: path + '.' + index, dbConnection: entity.connection })
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