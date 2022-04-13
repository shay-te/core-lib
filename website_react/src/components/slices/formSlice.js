import { createSlice } from '@reduxjs/toolkit';

export const formDataSlice = createSlice({
	name: 'forms',
	initialState: {
		fields: [],
	},
	reducers: {
		setFields: (state, action) => {
            state.fields = action.payload
        },
	},
});

export const {setFields} = formDataSlice.actions

export default formDataSlice.reducer