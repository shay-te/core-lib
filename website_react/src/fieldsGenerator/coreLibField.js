export const coreLibField = (yamlData) => {
    const fields = [];
    
    fields.push({
        title: 'Enter Core-Lib name',
        type: 'string',
        default_value: 'UserCoreLib',
        value: Object.keys(yamlData)[0],
        mandatory: true,
        // validatorCallback: validateFunc,
    })
    return fields
}