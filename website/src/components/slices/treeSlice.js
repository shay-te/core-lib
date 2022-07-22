import { current } from '@reduxjs/toolkit'
import { download, getValueAtPath } from "./../../utils/commonUtils";
import YAML from "yaml";
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";
import axios from 'axios';
import { downloadFile, toSnakeCase } from '../../utils/commonUtils';

const BASE = 'http://127.0.0.1:5000/';

const updateLocalStorage = (state) => {
    const recentCoreLibs = (JSON.parse(localStorage.getItem('core_libs')) === null ? [] : JSON.parse(localStorage.getItem('core_libs')))
    recentCoreLibs.splice(state.localStorageIndex, 1);
    recentCoreLibs.splice(state.localStorageIndex, 0, state.yaml);
    localStorage.setItem('core_libs', JSON.stringify(recentCoreLibs));
    localStorage.setItem('recent_core_lib', JSON.stringify(state.yaml))
}

const setTreeState = (state, yamlData) => {
    state.CoreLibName = yamlData.coreLibName
    updateLocalStorage(state)
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

const setNewEntryField = (path, state) => {
    if(!path.includes('function') && !path.includes('columns')){
        let newPath = `core_lib.${path}`
        if(path.includes('db_entities')){
            newPath = `core_lib.entities`
        }
        const newIndex = getValueAtPath(state.yaml, newPath.split('.')).length - 1
        return `${newPath}.${newIndex}`
    }
    return state.selectedField
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
        CoreLibName: '',
        yaml: {},
        fieldsTitle: '',
        fieldsPath: '',
        selectedConfig: '',
        selectedField: '',
        localStorageIndex: 0,
    },
    reducers: {
        init: (state, action) => {
            yamlData.init(action.payload)
            state.yaml = yamlData.toJSON()
            state.fields = []
            state.fieldsPath = ''
            state.fieldsTitle = ''
            state.selectedField = ''
            state.selectedConfig = ''
            setTreeState(state, yamlData)
        },
        downloadYaml: (state, action) => {
            const doc = new YAML.Document();
            doc.contents = state.yaml;
            download(doc.toString(), `${state.CoreLibName}.yaml`);
        },
        setList: (state, action) => {
            state.selectedConfig = action.payload
            state.selectedField = ''
        },
        setFields: (state, action) => {
            state.selectedField = action.payload.path
            state.fieldsPath = action.payload.path;
            state.fieldsTitle = action.payload.title
        },
        updateFields: (state, action) => {
            state.fieldsPath = yamlData.set(action.payload.path, action.payload.value, action.payload.env, action.payload.addOrRemove, action.payload.isBool)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
        },
        deleteTreeBranch: (state, action) => {
            if (action.payload === state.selectedField) {
                state.fieldsPath = ''
                state.fieldsTitle = ''
                state.selectedField = ''
            } else {
                const selectedArr = state.selectedField.split('.')
                const payloadArr = action.payload.split('.')
                const selectedIndex = selectedArr.at(-1)
                const payloadIndex = payloadArr.at(-1)
                if(selectedIndex > payloadIndex) {
                    selectedArr.splice(-1, 1)
                    selectedArr.push(parseInt(selectedIndex) - 1)
                    state.selectedField = selectedArr.join('.')
                }
            }
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
        },
        deleteFormField: (state, action) => {
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            updateLocalStorage(state)
        },
        addNewEntry: (state, action) => {
            createNewEntry(action.payload, yamlData)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
            state.selectedField = setNewEntryField(action.payload, state)
        },
        setStorageIndex: (state, action) => {
            state.localStorageIndex = action.payload;
        }
    },
})

export const { init, downloadYaml, setList, setFields, updateFields, deleteTreeBranch, addNewEntry, deleteFormField, setStorageIndex } = treeSlice.actions

export default treeSlice.reducer
