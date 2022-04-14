import { useEffect } from 'react';
import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';

function App() {
	const validateFunc = () => {
        console.log('validate');
    };

	const onFieldChange = (e, field) => {
        console.log(e, field)
    }

	return (
		<div className='app-root'>
			<Tree/>
			<Form onChange={onFieldChange}/>
		</div>
	);
}

export default App;
