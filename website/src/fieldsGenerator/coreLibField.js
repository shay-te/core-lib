export const coreLibField = (yamlData) => {
    const fields = [];
    
    fields.push({
        title: 'Enter Core-Lib name',
        type: 'string',
        default_value: 'UserCoreLib',
        value: yamlData.core_lib.name,
        mandatory: true,
        key: 'core_lib.name'
        // validatorCallback: validateFunc,
    })
    return fields
}