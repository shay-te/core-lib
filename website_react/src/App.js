import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';
import {
	init
} from "./components/slices/treeSlice";
import {useDispatch, useSelector} from "react-redux";
import { YamlData } from './components/utils/YamlData';

import { testInput } from './testInput';

function App() {
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch();
	dispatch(init(testInput))

	const onFieldChange = (field, e) => {
		if(field.key){
			const yamlClass = new YamlData(yamlData)
			const updatedData = yamlClass.set(field.key, e.target.value)
			dispatch(init(updatedData))
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
