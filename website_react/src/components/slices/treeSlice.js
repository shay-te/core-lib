import { current } from '@reduxjs/toolkit'

import { createSlice } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";
import { dataAccessFields } from '../../fieldsGenerator/dataAccessFields';
import { setupFields } from '../../fieldsGenerator/setupFields';
import { entityFields } from '../../fieldsGenerator/entityFields';

const setTreeState = (state, yamlData) => {
    state.dataAccess = yamlData.listChildrenUnderPath('data_layers.data_access')
    state.entities = yamlData.listChildrenUnderPath('data_layers.data')
    state.setup = yamlData.listChildrenUnderPath('setup')
    state.dbConnections = yamlData.listChildrenUnderPath('config.data')
    state.CoreLibName = yamlData.coreLibName
}

const pathToFields = (path, yaml) => {
    if (path.includes('data_layers.data_access.')) {
        return dataAccessFields(path, yaml);
    }
    if (path.includes('data_layers.data.')) {
        return entityFields(path, yaml);
    }
    if (path.includes('setup')) { return setupFields(yaml)}
    if (path.includes('data_layers.data_access')) {}
    if (path.includes('data_layers.data_access')) {}
	//coreLibField(yamlData)
	//dbConnectionFields(item, CoreLibName, yamlData)    
    return [];
}

const yamlData = new YamlData()
export const treeSlice = createSlice({
    name: 'tree',
    initialState: {
        dataAccess: [],
        dbConnections: [],
        entities: [],
        setup: [],
        CoreLibName: '',
        yaml: {},
        fields: [],
        fieldsPath: '',
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
            console.log('setFields:', action.payload, current(state.yaml))
            state.fieldsPath = action.payload;
            state.fields = pathToFields(action.payload, current(state.yaml))
        },
        updateFields: (state, action) => {
            console.log('updateFields', action.payload.value, typeof(action.payload.value))
            yamlData.set(action.payload.path, action.payload.value)
            state.yaml = yamlData.toJSON()
            state.fields = pathToFields(state.fieldsPath, state.yaml)
        }
    },
})

export const {init, updateTree, setFields, updateFields} = treeSlice.actions

export default treeSlice.reducer
