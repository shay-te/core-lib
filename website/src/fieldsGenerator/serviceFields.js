import { isPascalCase } from '../utils/validatorUtils';

export const serviceFields = (path, yamlData) => {
    const fields = []
    const dataAccess = ['']
    const pathSplit = path.split('.')
    const index = pathSplit.at(pathSplit.indexOf('services') + 1)
    const service = yamlData.core_lib.services[index]
    if(!service){
        return fields
    }
    const dataAccesses = yamlData.core_lib.data_accesses
    const keyPrefix = `core_lib.services.${index}`
    dataAccesses.forEach(da => {
        dataAccess.push(da.key)
    })
    fields.push({
        title: "Enter Service Name",
        type: "string",
        default_value: "",
        value: service.key,
        mandatory: true,
        key: `${keyPrefix}.key`,
        toolTipTitle: "Edit Service Name (PascalCase)",
        validatorCallback: isPascalCase,
    },
    {
        title: "DataAccess",
        type: "dropdown",
        default_value: dataAccess[0],
        value: service.data_access,
        mandatory: true,
        options: dataAccess,
        key: keyPrefix + '.data_access',
        toolTipTitle: "Select Data Access for this Service",
    },
    {
        title: "Functions",
        type: "functions",
        default_value: "",
        value: service.functions,
        mandatory: true,
        key: `${keyPrefix}.functions`,
    });
    return fields
};
