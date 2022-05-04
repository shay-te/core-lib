import { createSlice } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";

const getData = (state, yamlData) => {
    state.dataAccess = yamlData.listChildrenUnderPath('data_layers.data_access')
    state.entities = yamlData.listChildrenUnderPath('data_layers.data')
    state.setup = yamlData.listChildrenUnderPath('setup')
    state.dbConnections = yamlData.listChildrenUnderPath('config.data')
    state.CoreLibName = yamlData.coreLibName
}

export const treeSlice = createSlice({
    name: 'tree',
    initialState: {
        dataAccess: {},
        dbConnections: {},
        entities: {},
        setup: {},
        CoreLibName: '',
        yaml: {},
        yamlData: '',
    },
    reducers: {
        init: (state, action) => {
            let yamlData = new YamlData(action.payload)
            getData(state, yamlData)
            state.yaml = yamlData.toJSON()
        },
        updateField: (state, action) => {   
            let yamlData = new YamlData(action.payload)
            getData(state, yamlData)
            state.yaml = yamlData.toJSON()

        }
    },
})

export const {init, updateField} = treeSlice.actions

export default treeSlice.reducer
