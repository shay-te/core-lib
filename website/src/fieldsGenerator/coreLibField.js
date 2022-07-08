import { isPascalCase } from "../utils/validatorUtils";

export const coreLibField = (yamlData) => {
    const fields = [];
    fields.push({
        title: 'Enter Core-Lib name',
        type: 'string',
        default_value: 'UserCoreLib',
        value: yamlData.core_lib.name,
        mandatory: true,
        key: 'core_lib.name',
        toolTipTitle: "Edit Core-Lib Name (PascalCase)",
        validatorCallback: isPascalCase,
    })
    return fields
}