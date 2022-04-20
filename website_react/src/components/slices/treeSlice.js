import { createSlice } from '@reduxjs/toolkit'
import { getDataAccessList, YamlData } from "../utils/YamlData";

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
        // init function populate all states with class
        init: (state, action) => {
            let yamlData = new YamlData(action.payload)
            // yamlData.updateDataAccess('DetailsDataAccess')
            for (const clName in action.payload) {
                state.dataAccess = yamlData.getDataAccessList()
                state.entities = yamlData.getEntitiesList()
                state.setup = yamlData.getSetup()
                state.dbConnections = yamlData.getDBConnectionsList()
                state.CoreLibName = yamlData.coreLibName
                state.yaml = action.payload
            }
        },
        setDataAccess: (state, action) => {
            state.dataAccess = action.payload
        },
        setEntities: (state, action) => {
            state.entities = action.payload
        },
        setDBConnections: (state, action) => {
            state.dbConnections = action.payload
        },
        setSetup: (state, action) => {
            state.setup = action.payload
        },
        setCoreLibName: (state, action) => {
            state.CoreLibName = action.payload
        },
        setYaml: (state, action) => {
            state.yaml = action.payload
        },
        updateDataAccess: (state, action) => {
            console.log(action.payload)
        }
    },
})

export const {init, setDataAccess, setEntities, setDBConnections, setSetup, setCoreLibName, setYaml, updateDataAccess} = treeSlice.actions

export default treeSlice.reducer
