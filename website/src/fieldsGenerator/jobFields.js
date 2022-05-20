export const jobFields = (path, yamlData) => {
    const pathSplit = path.split('.')
    const index = pathSplit.at(pathSplit.indexOf('jobs')+1)
    const fields = []
    const keyPrefix = `core_lib.jobs.${index}`
    const job = yamlData.core_lib.jobs[index]
    fields.push({
        title: "Enter Job Name",
        type: "string",
        default_value: '',
        value: job.key,
        mandatory: true,
        key: `${keyPrefix}.key`,
        // validatorCallback: validateFunc,
    },
    {
        title: "Enter Initial Dealy",
        type: "string",
        default_value: '',
        value: job.initial_delay,
        mandatory: true,
        key: `${keyPrefix}.initial_delay`,
        // validatorCallback: validateFunc,
    },
    {
        title: "Enter Frequency for Job",
        type: "string",
        default_value: '',
        value: job.frequency,
        mandatory: true,
        key: `${keyPrefix}.frequency`,
        // validatorCallback: validateFunc,
    },
    )
    return fields
};
