import { current } from '@reduxjs/toolkit'

import { createSlice } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";
import { dataAccessFields } from '../../fieldsGenerator/dataAccessFields';
import { setupFields } from '../../fieldsGenerator/setupFields';
import { entityFields } from '../../fieldsGenerator/entityFields';
import { connectionFields } from '../../fieldsGenerator/connectionFields';
import { cacheFields } from '../../fieldsGenerator/cacheFields';
import { jobFields } from '../../fieldsGenerator/jobFields';
import { coreLibField } from '../../fieldsGenerator/coreLibField';

const setTreeState = (state, yamlData) => {
    state.dataAccess = yamlData.listChildrenUnderPath('core_lib.data_accesses')
    state.entities = yamlData.listChildrenUnderPath('core_lib.entities')
    state.setup = yamlData.listChildrenUnderPath('core_lib.setup')
    state.connections = yamlData.listChildrenUnderPath('core_lib.connections')
    state.jobs = yamlData.listChildrenUnderPath('core_lib.jobs')
    state.cache = yamlData.listChildrenUnderPath('core_lib.caches')
    state.CoreLibName = yamlData.coreLibName
}

const pathToFields = (path, yaml) => {
    if (path.includes('data_accesses')){ return dataAccessFields(path, yaml); }
    if (path.includes('entities')){ return entityFields(path, yaml); }
    if (path.includes('setup')){ return setupFields(yaml); }
    if (path.includes('connections') || path.includes('env')){ return connectionFields(path, yaml); }
    if (path.includes('caches') || path.includes('env')){ return cacheFields(path, yaml); }
    if (path.includes('jobs')){ return jobFields(path, yaml); }
    if (path.includes('name')){ return coreLibField(yaml); }
    return [];
}

const createNewEntry = (path, yamlData) => {
    if (path.includes('db_entity')){ return yamlData.createEntity(path.split('.')[1])}
    if (path.includes('data_accesses')){ return yamlData.createDataAccess()}
    if (path.includes('connections')){ return yamlData.createDBConnection()}
    if (path.includes('caches')){ return yamlData.createCache()}
    if (path.includes('jobs')){ return yamlData.createJob()}
    if (path.includes('columns')){ return yamlData.createColumn(path)}
    return [];
}

const yamlData = new YamlData()
export const treeSlice = createSlice({
    name: 'tree',
    initialState: {
        dataAccess: [],
        connections: [],
        entities: [],
        jobs: [],
        cache: [],
        setup: [],
        CoreLibName: '',
        yaml: {},
        fields: [],
        fieldsPath: '',
        treeState: {},
    },
    reducers: {
        init: (state, action) => {
            yamlData.init(action.payload)
            setTreeState(state, yamlData)
            state.yaml = yamlData.toJSON()
        },
        updateTree: (state, action) => {
            setTreeState(state, yamlData)
            state.yaml = yamlData.toJSON()
        },
        setFields: (state, action) => {
            state.fieldsPath = action.payload;
            state.fields = pathToFields(action.payload, current(state.yaml))
        },
        updateFields: (state, action) => {
            state.fieldsPath = yamlData.set(action.payload.path, action.payload.value, action.payload.env, action.payload.addOrRemove)
            state.yaml = yamlData.toJSON()
            state.fields = pathToFields(state.fieldsPath, state.yaml)
            setTreeState(state, yamlData)
        },
        deleteTreeBranch: (state, action) => {
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
        },
        deleteFormField: (state, action) => {
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            state.fields = pathToFields(state.fieldsPath, state.yaml)
        },
        addNewEntry: (state, action) => {
            createNewEntry(action.payload, yamlData)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
            state.fields = pathToFields(state.fieldsPath, state.yaml)
        },
        toggleCollapseExpand: (state, action) => {
            // if actionpath in tree state toggle else create path 
            if(!state.treeState.hasOwnProperty(action.payload)){
                state.treeState[action.payload] = true
            }
            else{
                state.treeState[action.payload] = !state.treeState[action.payload]
            }
            
        }
    },
})

export const { init, updateTree, setFields, updateFields, deleteTreeBranch, addNewEntry, toggleCollapseExpand, deleteFormField } = treeSlice.actions

export default treeSlice.reducer
