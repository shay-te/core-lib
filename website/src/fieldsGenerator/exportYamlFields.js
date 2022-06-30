import { downloadYaml } from "../components/slices/treeSlice";

export const exportYamlFields = () => {
    const fields = [];
    fields.push(
        {
            title: 'Export YAML file',
            subtitle: 'Will generate and download a new YAML file with the configured Core-Lib generator config.',
            type: 'title_subtitle',
            // validatorCallback: validateFunc,
        },
        {
            label: 'Export YAML',
            type: 'button',
            onClick: downloadYaml,
            // validatorCallback: validateFunc,
        },
    )
    return fields
}