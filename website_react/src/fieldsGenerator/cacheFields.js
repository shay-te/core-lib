import { getENVValue } from "../utils/commonUtils";

export const cacheFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const CoreLibName = pathSplit.at(0)
    const cacheName = pathSplit.at(pathSplit.indexOf('cache')+1) 
    const fields = []
    const dbConn = []
    const keyPrefix = CoreLibName + '.config.cache.' + cacheName
    const cache = yamlData[CoreLibName]['config']['cache'][cacheName]
    const envPrefix =  CoreLibName+'.env.'+cacheName.toUpperCase()
    fields.push({
        title: "Cache Name",
        type: "string",
        default_value: '',
        value: cacheName,
        mandatory: true,
        key: keyPrefix,
        // validatorCallback: validateFunc,
    },
    {
        title: "Cache Type",
        type: "dropdown",
        default_value: 'Memory',
        value: cache['type'],
        mandatory: true,
        options: [
            'memory',
            'memcached',
            'redis',
        ],
        key: keyPrefix + '.type',
        // validatorCallback: validateFunc,
    })
    if(cache['type'] !== 'memory'){
        fields.push(
            {
                title: "Enter the port no. of your cache server",
                type: "integer",
                default_value: null,
                value: getENVValue(cache["url"]["port"], yamlData),
                mandatory: true,
                key: `${keyPrefix}.url.port`,
                env: `${envPrefix}_PORT`,
                // validatorCallback: validateFunc,
            },
            {
                title: "Enter host of your cache server",
                type: "string",
                default_value: "localhost",
                value: getENVValue(cache["url"]["host"], yamlData),
                mandatory: true,
                key: `${keyPrefix}.url.host`,
                env: `${envPrefix}_HOST`,
                // validatorCallback: validateFunc,
            },
        )
    }
    if(cache['type'] === 'redis'){
        fields.push(
            {
                title: "Enter the protocol for redis",
                type: "string",
                default_value: 'redis',
                value: cache["url"]["protocol"],
                mandatory: true,
                key: `${keyPrefix}.url.protocol`,
                // validatorCallback: validateFunc,
            },
        )
    }
    return fields
};
