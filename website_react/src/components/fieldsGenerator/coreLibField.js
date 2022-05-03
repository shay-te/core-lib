export const coreLibField = (CoreLibName) => {
    const fields = [];

    fields.push({
        title: 'Enter Core-Lib name',
        type: 'string',
        default_value: 'UserCoreLib',
        value: CoreLibName,
        mandatory: true,
        // validatorCallback: validateFunc,
    })
    return fields
}