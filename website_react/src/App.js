import './App.scss';
import Form from './components/form/form';
import Tree from './components/tree/tree';

function App() {
	const validateFunc = () => {
        console.log('validate');
    };

	const data = {
		fields: [
			{
				title: 'Enter Core-Lib name',
				type: 'string',
				default_value: 'UserCoreLib',
				mandatory: true,
				validatorCallback: validateFunc,
			},
			// DB CONNECTION
			

			// // DB Entity
			// {
			// 	title: 'Enter the number of columns',
			// 	type: 'integer',
			// 	default_value: null,
			// 	mandatory: true,
			// 	validatorCallback: validateFunc,
			// },

			// {
			// 	title: 'Do you want SoftDelete?',
			// 	type: 'boolean',
			// 	default_value: false,
			// 	mandatory: true,
			// 	validatorCallback: validateFunc,
			// },
			// {
			// 	title: 'Enter the DataAccess name',
			// 	type: 'string',
			// 	default_value: 'UserDataAccess',
			// 	mandatory: true,
			// 	validatorCallback: validateFunc,
			// },
			// {
			// 	title: 'Enter entity name',
			// 	type: 'string',
			// 	default_value: 'User',
			// 	mandatory: true,
			// 	validatorCallback: validateFunc,
			// },
			// {
			// 	title: 'Select classifiers',
			// 	type: 'list',
			// 	default_value: 'Environment :: Console',
			// 	mandatory: true,
			// 	validatorCallback: validateFunc,
			// 	multiple_selection: true,
			// 	options: [
			// 		'Development Status :: 1 - Planning',
			// 		'Environment :: GPU',
			// 		'Environment :: Console',
			// 	],
			// },
		],
	};
	return (
		<div className='app-root'>
			<Tree/>
			<Form fields={data.fields}/>
		</div>
	);
}

export default App;
