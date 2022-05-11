import './App.scss';
import {
	init
} from "./components/slices/treeSlice";
import { useDispatch, useSelector } from "react-redux";

import { testInput } from './testInput';
import { useEffect } from 'react';
import {
	BrowserRouter as Router,
	Routes,
	Route
} from "react-router-dom";
import Editor from './pages/Editor';
import Document from './pages/Document'

function App() {
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch()

	useEffect(() => {
		if (JSON.stringify(yamlData) === '{}') {
			dispatch(init(testInput))
		}
		else {
			dispatch(init(yamlData))
		}

	}, [])


	return (
		<Router>
			<Routes>
				<Route exact path="/doc" element={<Document />}/>
				<Route exact path="/" element={<Editor />}/>
			</Routes>
		</Router>
	);
}

export default App;
