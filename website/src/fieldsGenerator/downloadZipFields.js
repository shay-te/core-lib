import { downloadZip } from "../components/slices/treeSlice";

export const downloadZipFields = () => {
    const fields = [];
    
    fields.push(
        {
            title: 'Download Core-Lib zip file',
            subtitle: 'Will generate and download a new Core-Lib zip file as configured in the generator. ' +
                      'After you have the zip file with you, you can then place the Core-Lib inside your project and start using it without any hassle.',
            type: 'title_subtitle',
        },
        {
            label: 'Download Zip',
            type: 'button',
            onClick: downloadZip,
        },
    )
    return fields
}