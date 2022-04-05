import InputString from '../inputs/InputString'
import InputInteger from '../inputs/InputInteger'
import InputBoolean from '../inputs/InputBoolean'
import InputENUM from '../inputs/InputENUM'
import InputList from '../inputs/InputList'

const DBEntityForm = () => {
    const validateFunc = () => {
        console.log('validate');
    };

    const data = {
        fields: [
            {
                title: 'Do you want to add entities to db connection?',
                type: 'boolean',
                default_value: true,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Enter the name of the database entity you\'d like to create',
                type: 'string',
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Do you want to add columns to entity?',
                type: 'boolean',
                default_value: true,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Enter the name of the column',
                type: 'string',
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Select datatype of column',
                type: 'list',
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
                multiple_selection: false,
                options: ['INTEGER', 'VARCHAR', 'BOOLEAN'],
            },
            {
                title: 'Enter the default value of column',
                type: 'string',
                default_value: null,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Do you want to implement Soft Delete?',
                type: 'boolean',
                default_value: false,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Do you want to implement Soft Delete Token?',
                type: 'boolean',
                default_value: false,
                mandatory: true,
                validatorCallback: validateFunc,
            },
            {
                title: 'Do you want to create a migration for entities?',
                type: 'boolean',
                default_value: false,
                mandatory: true,
                validatorCallback: validateFunc,
            },
        ]
    }

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
}

export default DBEntityForm