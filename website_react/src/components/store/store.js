import { configureStore } from '@reduxjs/toolkit';
import treeReducer from './../slices/treeSlice'
import formReducer from './../slices/formSlice'

export const store = configureStore({
	reducer: {
		treeData: treeReducer,
		formData: formReducer,
	},
    devTools: true,
});