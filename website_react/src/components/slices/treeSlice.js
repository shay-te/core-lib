import { createSlice } from '@reduxjs/toolkit'
import { YamlData } from "./../../utils/YamlData";

const setTreeState = (state, yamlData) => {
    state.dataAccess = yamlData.listChildrenUnderPath('data_layers.data_access')
    state.entities = yamlData.listChildrenUnderPath('data_layers.data')
    state.setup = yamlData.listChildrenUnderPath('setup')
    state.dbConnections = yamlData.listChildrenUnderPath('config.data')
    state.CoreLibName = yamlData.coreLibName
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
    },
    reducers: {
        init: (state, action) => {
            yamlData.init(action.payload)
            setTreeState(state, yamlData)
            state.yaml = yamlData.toJSON()
        },
        updateTree: (state, action) => {
            yamlData.set(action.payload.path, action.payload.value)
            setTreeState(state, yamlData)
            state.yaml = yamlData.toJSON()
        },
        setFields: (state, action) => {
            state.fields = action.payload
            
        },
    },
})

export const {init, updateTree, setFields} = treeSlice.actions

export default treeSlice.reducer
