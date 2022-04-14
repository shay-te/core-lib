import { createSlice } from '@reduxjs/toolkit'

export const treeSlice = createSlice({
    name: 'tree',
    initialState: {
        dataAccess: {},
        dbConnections: {},
        entities: {},
        setup: {},
        CoreLibName: '',
        yaml: {},
    },
    reducers: {
        // init function populate all states with class
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

export const {setDataAccess, setEntities, setDBConnections, setSetup, setCoreLibName, setYaml, updateDataAccess} = treeSlice.actions

export default treeSlice.reducer
