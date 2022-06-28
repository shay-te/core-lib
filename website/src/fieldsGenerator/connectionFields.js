import { getBoolean, getENVValue } from '../utils/commonUtils';

export const connectionFields = (path, yamlData) => {
    const fields = [];
    const pathSplit = path.split('.')
    const connections = yamlData.core_lib.connections
    const index = pathSplit.at(pathSplit.indexOf('connections') + 1)
    const connection = connections[index]
    const keyPrefix = `core_lib.connections.${index}`
    fields.push(
        {
            title: 'What is the name of the connection?',
            type: 'string',
            default_value: null,
            value: connection.key,
            mandatory: true,
            key: keyPrefix + '.key',
            // validatorCallback: validateFunc,
        },
        {
            title: 'Select connection',
            type: 'enum',
            mandatory: true,
            value: connection['type'].includes('SolrConnectionRegistry') ? 'solr' : connection['config']['url']['protocol'],
            // validatorCallback: validateFunc,
            options: [
                'SQLite',
                'Postgresql',
                'MySQL',
                'Oracle',
                'MSSQL',
                'Firebird',
                'Sybase',
                'Solr',
                'Neo4j'
            ],
            key: keyPrefix + '.config.url.protocol',
        },
        {
            title: 'Do you want to instantiate it via config?',
            type: 'boolean',
            default_value: false,
            value: getBoolean(connection['config_instantiate']),
            mandatory: true,
            key: keyPrefix + '.config_instantiate',
            // validatorCallback: validateFunc,
        },
    );
    if (!(['SolrConnectionRegistry', 'Neo4jConnectionRegistry'].some(val => connection['type'].includes(val)))) {
        fields.push(
            {
                title: 'Do you want to log queries?',
                type: 'boolean',
                default_value: false,
                value: connection['config']['log_queries'],
                mandatory: true,
                key: keyPrefix + '.config.log_queries',
                // validatorCallback: validateFunc,
            },
            {
                title: 'Do you want create Database?',
                type: 'boolean',
                default_value: true,
                value: connection['config']['create_db'],
                mandatory: true,
                key: keyPrefix + '.config.create_db',
                // validatorCallback: validateFunc,
            },
            {
                title: 'Enter the pool recycle time',
                type: 'integer',
                default_value: 3200,
                value: connection['config']['session']['pool_recycle'],
                mandatory: true,
                key: keyPrefix + '.config.session.pool_recycle',
                // validatorCallback: validateFunc,
            },
            {
                title: 'Do you want to set pool pre ping?',
                type: 'boolean',
                default_value: false,
                value: connection['config']['session']['pool_pre_ping'],
                mandatory: true,
                key: keyPrefix + '.config.session.pool_pre_ping',
                // validatorCallback: validateFunc,
            }
        );
    }
    const envPrefix = `core_lib.env.${connection.key.toUpperCase()}`
    if (connection['config']['url']['protocol'].toLowerCase() !== 'sqlite') {
        fields.push(
            {
                title: 'Enter the port no. of your connection',
                type: 'integer',
                default_value: null,
                value: getENVValue(connection['config']['url']['port'], yamlData),
                mandatory: true,
                key: `${keyPrefix}.config.url.port`,
                env: `${envPrefix}_PORT`,
                // validatorCallback: validateFunc,
            },
            {
                title: 'Enter host of your connection',
                type: 'string',
                default_value: 'localhost',
                value: getENVValue(connection['config']['url']['host'], yamlData),
                mandatory: true,
                key: `${keyPrefix}.config.url.host`,
                env: `${envPrefix}_HOST`,
                // validatorCallback: validateFunc,
            },
        );
        if (!connection['type'].includes('Neo4jConnectionRegistry')) {
            fields.push(
                {
                    title: 'Enter filename for your connection',
                    type: 'string',
                    default_value: 'file',
                    value: getENVValue(connection['config']['url']['file'], yamlData),
                    mandatory: true,
                    key: `${keyPrefix}.config.url.file`,
                    env: `${envPrefix}_DB`,
                    // validatorCallback: validateFunc,
                },
            )
        }
        if (['SqlAlchemyConnectionRegistry', 'Neo4jConnectionRegistry'].some(val => connection['type'].includes(val))) {
            fields.push(
                {
                    title: 'Enter your connection username',
                    type: 'string',
                    default_value: 'user',
                    value: connection['type'].includes('SqlAlchemyConnectionRegistry') ? 
                            getENVValue(connection['config']['url']['username'], yamlData) : 
                            getENVValue(connection['config']['credentials']['username'], yamlData),
                    mandatory: true,
                    key: connection['type'].includes('SqlAlchemyConnectionRegistry') ? `${keyPrefix}.config.url.username` : `${keyPrefix}.config.credentials.username`,
                    env: `${envPrefix}_USER`,
                    // validatorCallback: validateFunc,
                },
                {
                    title: 'Enter your connection password',
                    type: 'string',
                    default_value: null,
                    value: connection['type'].includes('SqlAlchemyConnectionRegistry') ? 
                            getENVValue(connection['config']['url']['password'], yamlData) : 
                            getENVValue(connection['config']['credentials']['password'], yamlData),
                    mandatory: true,
                    key: connection['type'].includes('SqlAlchemyConnectionRegistry') ? `${keyPrefix}.config.url.password` : `${keyPrefix}.config.credentials.password`,
                    env: `${envPrefix}_PASSWORD`,
                    // validatorCallback: validateFunc,
                }
            )
        }
    }
    return fields
}