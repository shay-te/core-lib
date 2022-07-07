import { dataAccessFields } from '../fieldsGenerator/dataAccessFields';
import { setupFields } from '../fieldsGenerator/setupFields';
import { entityFields } from '../fieldsGenerator/entityFields';
import { connectionFields } from '../fieldsGenerator/connectionFields';
import { cacheFields } from '../fieldsGenerator/cacheFields';
import { serviceFields } from '../fieldsGenerator/serviceFields';
import { jobFields } from '../fieldsGenerator/jobFields';
import { coreLibField } from '../fieldsGenerator/coreLibField';
import { exportYamlFields } from '../fieldsGenerator/exportYamlFields';
import { downloadZipFields } from '../fieldsGenerator/downloadZipFields';


export default class FieldsFactory{
    generate(path, yamlData){
        if (path.includes('data_accesses')) { return dataAccessFields(path, yamlData); }
        if (path.includes('entities')) { return entityFields(path, yamlData); }
        if (path.includes('setup')) { return setupFields(yamlData); }
        if (path.includes('connections') || path.includes('env')) { return connectionFields(path, yamlData); }
        if (path.includes('caches') || path.includes('env')) { return cacheFields(path, yamlData); }
        if (path.includes('services')) { return serviceFields(path, yamlData); }
        if (path.includes('jobs')) { return jobFields(path, yamlData); }
        if (path.includes('name')) { return coreLibField(yamlData); }
        if (path.includes('export_yaml')) { return exportYamlFields(); }
        if (path.includes('download_zip')) { return downloadZipFields(); }
        return [];
    }
}