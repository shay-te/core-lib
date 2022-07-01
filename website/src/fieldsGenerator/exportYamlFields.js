import { downloadYaml } from "../components/slices/treeSlice";

export const exportYamlFields = () => {
    const fields = [];
    fields.push(
        {
            title: 'Export YAML file',
            subtitle: 'Will generate and download a new YAML file with the configured Core-Lib generator config. ' +
                      'This YAML contains the data that will help the generator generate a new Core-Lib for you. ' +
                      'You can either select the Download Zip option and download the zip file of your Core-Lib right away or '+
                      'you can use the command `core_lib -g YourCoreLib.yaml` to generate a new Core-Lib from the command line.',
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