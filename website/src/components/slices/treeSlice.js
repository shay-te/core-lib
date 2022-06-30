import { current } from '@reduxjs/toolkit'
import { download } from "./../../utils/commonUtils";
import YAML from "yaml";
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";
import { dataAccessFields } from '../../fieldsGenerator/dataAccessFields';
import { setupFields } from '../../fieldsGenerator/setupFields';
import { entityFields } from '../../fieldsGenerator/entityFields';
import { connectionFields } from '../../fieldsGenerator/connectionFields';
import { cacheFields } from '../../fieldsGenerator/cacheFields';
import { serviceFields } from '../../fieldsGenerator/serviceFields';
import { jobFields } from '../../fieldsGenerator/jobFields';
import { coreLibField } from '../../fieldsGenerator/coreLibField';
import axios from 'axios';
import { downloadFile, toSnakeCase } from '../../utils/commonUtils';
import { exportYamlFields } from '../../fieldsGenerator/exportYamlFields';
import { downloadZipFields } from '../../fieldsGenerator/downloadZipFields';

const BASE = 'http://127.0.0.1:5000/';

const updateLocalStorage = (state) => {
    const recentCoreLibs = (JSON.parse(localStorage.getItem('core_libs')) === null ? [] : JSON.parse(localStorage.getItem('core_libs')))
    recentCoreLibs.splice(state.localStorageIndex, 1);
    recentCoreLibs.splice(state.localStorageIndex, 0, state.yaml);
    localStorage.setItem('core_libs', JSON.stringify(recentCoreLibs));
    localStorage.setItem('recent_core_lib', JSON.stringify(state.yaml))
}

const setTreeState = (state, yamlData) => {
    state.dataAccess = yamlData.listChildrenUnderPath('core_lib.data_accesses')
    state.entities = yamlData.listChildrenUnderPath('core_lib.entities')
    state.setup = yamlData.listChildrenUnderPath('core_lib.setup')
    state.connections = yamlData.listChildrenUnderPath('core_lib.connections')
    state.jobs = yamlData.listChildrenUnderPath('core_lib.jobs')
    state.cache = yamlData.listChildrenUnderPath('core_lib.caches')
    state.services = yamlData.listChildrenUnderPath('core_lib.services')
    state.CoreLibName = yamlData.coreLibName
    updateLocalStorage(state)
}

const pathToFields = (path, yaml) => {
    if (path.includes('data_accesses')) { return dataAccessFields(path, yaml); }
    if (path.includes('entities')) { return entityFields(path, yaml); }
    if (path.includes('setup')) { return setupFields(yaml); }
    if (path.includes('connections') || path.includes('env')) { return connectionFields(path, yaml); }
    if (path.includes('caches') || path.includes('env')) { return cacheFields(path, yaml); }
    if (path.includes('services')) { return serviceFields(path, yaml); }
    if (path.includes('jobs')) { return jobFields(path, yaml); }
    if (path.includes('name')) { return coreLibField(yaml); }
    if (path.includes('export_yaml')) { return exportYamlFields(yaml); }
    if (path.includes('download_zip')) { return downloadZipFields(yaml); }
    return [];
}

const createNewEntry = (path, yamlData) => {
    if (path.includes('functions')) { return yamlData.createFunction(path) }
    if (path.includes('db_entities')) { return yamlData.createEntity(path.split('.')[1]) }
    if (path.includes('data_accesses')) { return yamlData.createDataAccess() }
    if (path.includes('connections')) { return yamlData.createConnection() }
    if (path.includes('caches')) { return yamlData.createCache() }
    if (path.includes('jobs')) { return yamlData.createJob() }
    if (path.includes('columns')) { return yamlData.createColumn(path) }
    if (path.includes('services')) { return yamlData.createServices() }
    return [];
}

const resetFields = (state, path) => {
    if (path === state.fieldsPath || path.includes('connections')) {
        state.fields = []
        state.fieldsPath = ''
        state.fieldsTitle = ''
    }
}

const yamlData = new YamlData()

export const downloadZip = createAsyncThunk(
	'api/downloadZip',
	async (_, { getState }) => {
        const state = getState();
		const url = BASE + 'api/download_zip';
		const response = await axios.post(url, {config: state.treeData.yaml}, { responseType: 'blob' });
        downloadFile(response.data, `${toSnakeCase(state.treeData.CoreLibName)}.zip`);
	}
)

export const treeSlice = createSlice({
    name: 'tree',
    initialState: {
        dataAccess: [],
        connections: [],
        entities: [],
        jobs: [],
        cache: [],
        services: [],
        setup: [],
        CoreLibName: '',
        yaml: {},
        fields: [],
        fieldsTitle: '',
        fieldsPath: '',
        selectedConfig: '',
        selectedField: '',
        treeSelected: {},
        treeState: {},
        localStorageIndex: 0,
    },
    reducers: {
        init: (state, action) => {
            yamlData.init(action.payload)
            state.yaml = yamlData.toJSON()
            state.fields = []
            state.fieldsPath = ''
            state.fieldsTitle = ''
            setTreeState(state, yamlData)
        },
        downloadYaml: (state, action) => {
            const doc = new YAML.Document();
            doc.contents = state.yaml;
            download(doc.toString(), `${state.CoreLibName}.yaml`);
        },
        setList: (state, action) => {
            state.selectedConfig = action.payload
        },
        setFields: (state, action) => {
            state.selectedField = action.payload.path
            state.fieldsPath = action.payload.path;
            state.fields = pathToFields(action.payload.path, current(state.yaml))
            state.fieldsTitle = action.payload.title
        },
        updateFields: (state, action) => {
            state.fieldsPath = yamlData.set(action.payload.path, action.payload.value, action.payload.env, action.payload.addOrRemove, action.payload.isBool)
            state.yaml = yamlData.toJSON()
            state.fields = pathToFields(state.fieldsPath, state.yaml)
            setTreeState(state, yamlData)
        },
        deleteTreeBranch: (state, action) => {
            resetFields(state, action.payload)
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
        },
        deleteFormField: (state, action) => {
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            state.fields = pathToFields(state.fieldsPath, state.yaml)
            updateLocalStorage(state)
        },
        addNewEntry: (state, action) => {
            createNewEntry(action.payload, yamlData)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
            state.fields = pathToFields(state.fieldsPath, state.yaml)
            state.treeState[action.payload] = false
        },
        toggleCollapseExpand: (state, action) => {
            if (!state.treeState.hasOwnProperty(action.payload)) {
                state.treeState[action.payload] = true
            }
            else {
                state.treeState[action.payload] = !state.treeState[action.payload]
            }

        },
        toggleSelected: (state, action) => {
            state.treeSelected = {}
            state.treeSelected[action.payload] = true
        },
        setStorageIndex: (state, action) => {
            state.localStorageIndex = action.payload;
        }
    },
})

export const { init, downloadYaml, setList, setFields, updateFields, deleteTreeBranch, addNewEntry, toggleCollapseExpand, deleteFormField, toggleSelected, setStorageIndex } = treeSlice.actions

export default treeSlice.reducer
