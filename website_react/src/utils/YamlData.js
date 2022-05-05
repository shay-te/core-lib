import { isObject } from "./commonUtils"

export class YamlData {

    init(data) {
        this.yaml = data
        this.coreLibName = Object.keys(data)[0]
    }

    set(path, value) {
        const data = JSON.parse(JSON.stringify(this.yaml))
        const steps = path.split(".")
        if(steps.length === 1 && steps[0] === 'CoreLibName'){
            data[value] = data[this.coreLibName]
            delete data[this.coreLibName]
            this.yaml = data
            this.coreLibName = value
        }
        else{
            const objField = steps.reduce((key, val) => key && key[val] ? key[val] : '', data);
            const fieldName = steps[steps.length - 1]
            if (isObject(objField)) {
                const oldKeyName = steps[steps.length - 1]
                const parent = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
                parent[value] = parent[oldKeyName];
                delete parent[oldKeyName]
                this.yaml = data
                steps[steps.length - 1] = value
                return steps.join('.')
            } else {
                const parent = steps.slice(0, -1).reduce((key, val) => key && key[val] ? key[val] : '', data);
                parent[fieldName] = value;
                this.yaml = data
            }
        }
        return path
    }

    get(path) {
        return path.split('.').reduce((obj, key) => {
            return obj && obj[key];
        }, this.yaml);
    }

    listChildrenUnderPath(path) {
        const res = []
        const new_path = this.coreLibName + '.' + path
        const list = this.get(new_path)
        if(path === 'data_layers.data'){
            const entity_res = []
            Object.keys(list).forEach((dbConn, index) => {
                const entity_dbconn_path = new_path+'.'+dbConn
                const entity_list = this.get(entity_dbconn_path)
                entity_res.push({[dbConn]: []})
                Object.keys(entity_list).forEach(entity => {
                    if(entity !== 'migrate'){
                        entity_res[index][dbConn].push({name: entity, path: entity_dbconn_path+'.'+entity, dbConnection: dbConn})
                    }
                })
            })
            return entity_res
        }
        Object.keys(list).forEach(item => {
            res.push({name: item, path: new_path+'.'+item})
        })
        return res
    }

    toJSON() {
        return this.yaml
    }
}