import { useEffect } from 'react';
import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';
import {
	init
} from "./components/slices/treeSlice";
import {useDispatch, useSelector} from "react-redux";
import { YamlData } from './components/utils/YamlData';



import { testInput } from './testInput';
import TreeSection from './components/TreeSection/TreeSection';

function App() {
	const clName = useSelector((state) => state.treeData.CoreLibName);
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch();
	

	useEffect(() => {
		dispatch(init(testInput))
	}, []);

	const onFieldChange = (field, e) => {
		if(field.key){
			const yamlClass = new YamlData(yamlData)
			yamlClass.listChildrenUnderPath('data_layers.data_access')
			const updatedData = yamlClass.set(field.key, e.target.value)
			// dispatch(init(updatedData))
			console.log(updatedData) // just to check for now
		}
    }
	return (
		<div className='app-root'>
			{/* <Tree/>
			<Form onChange={onFieldChange}/> */}
			<div >asdasda</div>
			<TreeSection title='adada' items={['asdasd', 'asdasddas']} path='dataaccess.'/>
		</div>
	);
}

export default App;
