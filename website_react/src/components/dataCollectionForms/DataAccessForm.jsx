import InputString from '../inputs/InputString'
import InputInteger from '../inputs/InputInteger'
import InputBoolean from '../inputs/InputBoolean'
import InputENUM from '../inputs/InputENUM'
import InputList from '../inputs/InputList'


const DataAccessForm = () => {
    const validateFunc = () => {
        console.log('validate');
    };
    
    const data = {
        fields: [
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
                default_value: "SQLite",
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
        ],
    };
	return (
		<>
			{data.fields.map((field, index) => {
				switch (field.type) {
					case "string":
						return (
							<InputString
								formFields={field}
								index={index}
								key={index}
							/>
						);
					case "integer":
						return (
							<InputInteger
								formFields={field}
								index={index}
								key={index}
							/>
						);
					case "boolean":
						return (
							<InputBoolean
								formFields={field}
								index={index}
								key={index}
							/>
						);
					case "enum":
						return (
							<InputENUM
								formFields={field}
								index={index}
								key={index}
							/>
						);
					case "list":
						return (
							<InputList
								formFields={field}
								index={index}
								key={index}
							/>
						);
				}
			})}
		</>
	);
};

export default DataAccessForm