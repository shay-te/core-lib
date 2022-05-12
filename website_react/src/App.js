import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';
import {
	init,
	updateFields
} from "./components/slices/treeSlice";
import { useDispatch, useSelector } from "react-redux";

import { testInput } from './testInput';
import { useEffect, useState } from 'react';

function App() {
	const yamlData = useSelector((state) => state.treeData.yaml);
	const formFields = useSelector((state) => state.treeData.fields);
	const dispatch = useDispatch()

	useEffect(() => {
		if (JSON.stringify(yamlData) === '{}') {
			dispatch(init(testInput))
		}
		else {
			dispatch(init(yamlData))
		}

	}, [])

	const onFieldChange = (field, e) => {
		if (field.key) {
			dispatch(updateFields({ path: field.key, value: e.target.value, env: field.env }))
		}
	}
	return (
		<div className='app-root'>
			<Tree key={'tree'}/>
			<Form onChange={onFieldChange} />
		</div>
	);
}

export default App;
