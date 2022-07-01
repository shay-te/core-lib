import { isNotNull, isSnakeCase, isTimeFrame } from "../utils/validatorUtils";

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
        toolTipTitle: "Edit Job Name (snake_case)",
        validatorCallback: isSnakeCase,
    },
    {
        title: "Enter Initial Dealy",
        type: "string",
        default_value: '',
        value: job.initial_delay,
        mandatory: true,
        key: `${keyPrefix}.initial_delay`,
        helperText: "Initial delay for the job (boot, startup, 1s, 1m, 1h, 1h30m ...)",
        validatorCallback: isTimeFrame,
    },
    {
        title: "Enter Frequency for Job",
        type: "string",
        default_value: '',
        value: job.frequency,
        mandatory: false,
        key: `${keyPrefix}.frequency`,
        helperText: "Frequency of the job (1s, 1m, 1h, 1h30m ...)",
        validatorCallback: isTimeFrame,
    },
    )
    return fields
};
