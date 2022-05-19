import { current } from '@reduxjs/toolkit'

import { createSlice } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";
import { dataAccessFields } from '../../fieldsGenerator/dataAccessFields';
import { setupFields } from '../../fieldsGenerator/setupFields';
import { entityFields } from '../../fieldsGenerator/entityFields';
import { dbConnectionFields } from '../../fieldsGenerator/dbConnectionFields';
import { cacheFields } from '../../fieldsGenerator/cacheFields';
import { jobFields } from '../../fieldsGenerator/jobFields';
import { coreLibField } from '../../fieldsGenerator/coreLibField';

const setTreeState = (state, yamlData) => {
    state.dataAccess = yamlData.listChildrenUnderPath('data_layers.data_access')
    state.entities = yamlData.listChildrenUnderPath('data_layers.data')
    state.setup = yamlData.listChildrenUnderPath('setup')
    state.dbConnections = yamlData.listChildrenUnderPath('config.data')
    state.jobs = yamlData.listChildrenUnderPath('config.jobs')
    state.cache = yamlData.listChildrenUnderPath('config.cache')
    state.CoreLibName = yamlData.coreLibName
}

const pathToFields = (path, yaml) => {
    if (path.includes('data_layers.data_access')){ return dataAccessFields(path, yaml); }
    if (path.includes('data_layers.data')){ return entityFields(path, yaml); }
    if (path.includes('setup')){ return setupFields(yaml); }
    if (path.includes('config.data') || path.includes('env')){ return dbConnectionFields(path, yaml); }
    if (path.includes('config.cache') || path.includes('env')){ return cacheFields(path, yaml); }
    if (path.includes('config.jobs')){ return jobFields(path, yaml); }
    if (path.includes('CoreLibName')){ return coreLibField(yaml); }
    return [];
}

const createNewEntry = (path, yamlData) => {
    if (path.includes('db_entity')){ return yamlData.createEntity(path.split('.')[1])}
    if (path.includes('data_access')){ return yamlData.createDataAccess()}
    if (path.includes('db_connection')){ return yamlData.createDBConnection()}
    if (path.includes('config.cache')){ return yamlData.createCache()}
    if (path.includes('config.jobs')){ return yamlData.createJob()}
    return [];
}

const yamlData = new YamlData()
export const treeSlice = createSlice({
    name: 'tree',
    initialState: {
        dataAccess: [],
        dbConnections: [],
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
            state.fieldsPath = yamlData.set(action.payload.path, action.payload.value, action.payload.env)
            state.yaml = yamlData.toJSON()
            state.fields = pathToFields(state.fieldsPath, state.yaml)
            setTreeState(state, yamlData)
        },
        deleteTreeBranch: (state, action) => {
            yamlData.delete(action.payload)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
        },
        addNewEntry: (state, action) => {
            createNewEntry(action.payload, yamlData)
            state.yaml = yamlData.toJSON()
            setTreeState(state, yamlData)
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

export const { init, updateTree, setFields, updateFields, deleteTreeBranch, addNewEntry, toggleCollapseExpand } = treeSlice.actions

export default treeSlice.reducer
