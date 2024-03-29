import { getENVValue } from "../utils/commonUtils";
import { isNotNull, isNumber, isSnakeCase } from "../utils/validatorUtils";

export const cacheFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const index = pathSplit.at(pathSplit.indexOf('caches')+1)
    const fields = []
    const keyPrefix = `core_lib.caches.${index}`
    const cache = yamlData.core_lib.caches[index]
    if(!cache){
        return fields
    }
    const cacheName = yamlData.core_lib.caches[index].key
    const envPrefix =  `core_lib.env.${cacheName.toUpperCase()}`
    fields.push({
        title: "Enter Cache Name",
        type: "string",
        default_value: '',
        value: cacheName,
        mandatory: true,
        key: `${keyPrefix}.key`,
        toolTipTitle: "Edit Cache Name (snake_case)",
        validatorCallback: isSnakeCase,
    },
    {
        title: "Select Cache Type",
        type: "dropdown",
        default_value: 'Memory',
        value: cache.type,
        mandatory: true,
        options: [
            'memory',
            'memcached',
            'redis',
        ],
        key: `${keyPrefix}.type`,
        toolTipTitle: "Select type of your cache for this Core-Lib",
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
                validatorCallback: isNumber,
            },
            {
                title: "Enter host of your cache server",
                type: "string",
                default_value: "localhost",
                value: getENVValue(cache["url"]["host"], yamlData),
                mandatory: true,
                key: `${keyPrefix}.url.host`,
                env: `${envPrefix}_HOST`,
                validatorCallback: isNotNull,
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
                validatorCallback: isNotNull,
            },
        )
    }
    return fields
};
