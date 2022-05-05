import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';
import {
	init,
	updateTree
} from "./components/slices/treeSlice";
import {useDispatch, useSelector} from "react-redux";

import { testInput } from './testInput';
import { useEffect } from 'react';
import { updateFields } from './components/slices/treeSlice';

function App() {
	const yamlData = useSelector((state) => state.treeData.yaml);
	const formFields = useSelector((state) => state.treeData.fields);
	const dispatch = useDispatch()

	useEffect(() => {
		if(JSON.stringify(yamlData) === '{}'){
			dispatch(init(testInput))
		}
		else{
			dispatch(init(yamlData))
		}
		
	}, [])

	const onFieldChange = (field, e) => {
		if(field.key){
			dispatch(updateFields({path: field.key, value: e.target.value}))
			// dispatch(updateTree({path: field.key, value: e.target.value}))
			// formFields.forEach((formField, index) => {
			// 	if(formField.key === field.key){
			// 		const tempField = JSON.parse(JSON.stringify(field))
			// 		const tempFormFields = JSON.parse(JSON.stringify(formFields))
			// 		tempField.value = e.target.value
			// 		tempFormFields.splice(index, 1)
			// 		tempFormFields.splice(index, 0, tempField)
			// 		dispatch(setFields(tempFormFields))
			// 	}
			// })
		}
    }
	return (
		<div className='app-root'>
			<Tree/>
			<Form onChange={onFieldChange}/>
		</div>
	);
}

export default App;
