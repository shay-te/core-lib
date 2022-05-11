export const jobFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const CoreLibName = pathSplit.at(0)
    const jobName = pathSplit.at(pathSplit.indexOf('jobs')+1) 
    const fields = []
    const keyPrefix = CoreLibName + '.config.jobs.' + jobName
    const job = yamlData[CoreLibName]['config']['jobs'][jobName]
    fields.push({
        title: "Job Name",
        type: "string",
        default_value: '',
        value: jobName,
        mandatory: true,
        key: keyPrefix,
        // validatorCallback: validateFunc,
    },
    {
        title: "Frequency",
        type: "string",
        default_value: '',
        value: job['frequency'],
        mandatory: true,
        key: keyPrefix + '.frequency',
        // validatorCallback: validateFunc,
    },
    )
    return fields
};
