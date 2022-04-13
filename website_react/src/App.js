import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';

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
			{
                title: "What is the name of the DB connection?",
                type: "string",
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Select DB connection",
                type: "enum",
                mandatory: true,
                validatorCallback: validateFunc,
                options: [
                    "SQLite",
                    "Postgresql",
                    "MySQL",
                    "Oracle",
                    "MSSQL",
                    "Firebird",
                    "Sybase",
                    "MongoDB",
                ],
            },
            {
                title: "Do you want to log queries?",
                type: "boolean",
                default_value: false,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Do you want create Database?",
                type: "boolean",
                default_value: true,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Enter the pool recycle time",
                type: "integer",
                default_value: 3200,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Do you want to set pool pre ping?",
                type: "boolean",
                default_value: false,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Enter the port no. of your DB",
                type: "integer",
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Enter host of your DB",
                type: "string",
                default_value: "localhost",
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Enter your DB username",
                type: "string",
                default_value: "user",
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: "Enter your DB password",
                type: "string",
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
            },
			{
				title: 'Select classifiers',
				type: 'list',
				default_value: 'Environment :: Console',
				mandatory: true,
				validatorCallback: validateFunc,
				multiple_selection: true,
				options: [
					'Development Status :: 1 - Planning',
					'Environment :: GPU',
					'Environment :: Console',
				],
			},
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
