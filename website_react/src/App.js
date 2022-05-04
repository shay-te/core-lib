import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';
import {
	init,
	updateField
} from "./components/slices/treeSlice";
import {useDispatch, useSelector} from "react-redux";
import { YamlData } from './utils/YamlData';

import { testInput } from './testInput';
import { useEffect, useMemo } from 'react';

function App() {
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch()
	useMemo(() => {
		if(JSON.stringify(yamlData) === '{}'){
			dispatch(init(testInput))
		}
		else{
			dispatch(init(yamlData))
		}
		
	})

	const onFieldChange = (field, e) => {
		if(field.key){
			console.log(field)
			const yamlClass = new YamlData(yamlData)
			const updatedData = yamlClass.set(field.key, e.target.value)
			dispatch(updateField(updatedData))
			console.log(updatedData) // just to check for now
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
