export default class Pathsfactory{
    _get(path, yaml) {
        return path.split('.').reduce((obj, key) => {
            return obj && obj[key];
        }, yaml);
    }

    listPaths(path, yaml) {
        const res = []
        const list = this._get(path, yaml) 
        
        if(!list){
            return res
        }
        if (path === 'core_lib.entities') {
            const entityRes = []
            const connectionList = this._get('core_lib.connections', yaml)
            connectionList.forEach((connection) => {
                if(connection.type.includes('SqlAlchemyConnectionRegistry')) {
                    const entities = []
                    list.forEach((entity, index) => {
                        if(connection.key === entity.connection){
                            entities.push({ name: `${entity.key}`, path: path + '.' + index, dbConnection: entity.connection })
                        }
                        
                    })
                    entityRes.push({connection: connection.key, entities})
                }
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
}