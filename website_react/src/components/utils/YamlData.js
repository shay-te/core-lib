export class YamlData {
    constructor(data) {
        this.yaml = data
        this.coreLibName = Object.keys(data)[0]
    }

    set(path, value) {
        var data = JSON.parse(JSON.stringify(this.yaml));
        var steps = path.split(".");
        var fieldName = steps.splice(steps.length - 1, 1);
        var objField = steps.reduce((key, val) => key && key[val] ? key[val] : '', data);
        objField[fieldName] = value;
        return data
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
            Object.keys(list).map((dbConn, index) => {
                const entity_dbconn_path = new_path+'.'+dbConn
                const entity_list = this.get(entity_dbconn_path)
                entity_res.push({[dbConn]: []})
                Object.keys(entity_list).map(entity => {
                    entity_res[index][dbConn].push({name: entity, path: entity_dbconn_path+'.'+entity, dbConnection: dbConn})
                })
            })
            return entity_res
        }
        Object.keys(list).map(item => {
            res.push({name: item, path: new_path+'.'+item})
        })
        return res
    }

    toJSON() {
        return this.yaml
    }
}