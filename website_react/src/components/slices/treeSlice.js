import { createSlice } from '@reduxjs/toolkit'
import { YamlData } from "../utils/YamlData";

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
            state.dataAccess = yamlData.listChildrenUnderPath('data_layers.data_access')
            state.entities = yamlData.listChildrenUnderPath('data_layers.data')
            state.setup = yamlData.listChildrenUnderPath('setup')
            state.dbConnections = yamlData.listChildrenUnderPath('config.data')
            state.CoreLibName = yamlData.coreLibName
            state.yaml = action.payload
        }
    },
})

export const {init, setDataAccess, setEntities, setDBConnections, setSetup, setCoreLibName, setYaml, updateDataAccess} = treeSlice.actions

export default treeSlice.reducer
