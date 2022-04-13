import { createSlice } from '@reduxjs/toolkit';

const initialState = {
	status: 'idle',
	formData: [],
};

export const formDataSlice = createSlice({
	name: 'forms',
	initialState,
	reducers: {	},
});