import { useDispatch, useSelector } from "react-redux";
import { setFields } from "../slices/formSlice";
import { hideContents } from "../utils/commonUtils";

const RenderSetup = () => {
	const setup = useSelector((state) => state.treeData.setup);
	const dispatch = useDispatch()

	const setFormFields = () => {
		console.log(setup)
		const fields = []
		fields.push({
            title: "Your Full Name",
            type: "string",
            default_value: setup.author,
            mandatory: true,
            // validatorCallback: validateFunc,
        })
		fields.push({
            title: "Your Email",
            type: "string",
            default_value: setup.author_email,
            mandatory: true,
            // validatorCallback: validateFunc,
        })
		fields.push({
			title: 'Select classifiers',
			type: 'list',
			default_value: setup.classifiers,
			mandatory: true,
			// validatorCallback: validateFunc,
			multiple_selection: true,
			options: [
				'Development Status :: 3 - Alpha',
				'Development Status :: 4 - Beta',
				'Development Status :: 5 - Production/Stable',
				'Environment :: MacOS X',
				'Environment :: Win32 (MS Windows)',
				'Framework :: Django :: 4.0',
				'Framework :: Flask',
				'Framework :: Jupyter',
				'Natural Language :: English',
				'Operating System :: OS Independent',
				'Programming Language :: Python :: 3.7',
				'Topic :: Software Development',
				'Topic :: Software Development :: Libraries',
				'Topic :: Software Development :: Libraries :: Python Modules',
				'Typing :: Typed',
			],
		})
		fields.push({
            title: "Project Description",
            type: "string",
            default_value: setup.description,
            mandatory: true,
            // validatorCallback: validateFunc,
        })
		fields.push({
            title: "License Type",
            type: "enum",
            default_value: setup.license,
            mandatory: true,
			options:[
				'MIT', 
				'APACHE_LICENSE_2', 
				'MOZILLA_PUBLIC_LICENSE_2',
			]
            // validatorCallback: validateFunc,
        })
		fields.push({
            title: "Project url",
            type: "string",
            default_value: setup.url,
            mandatory: false,
            // validatorCallback: validateFunc,
        })
		fields.push({
            title: "Project version",
            type: "string",
            default_value: setup.version,
            mandatory: false,
            // validatorCallback: validateFunc,
        })
		// fields.push({
        //     title: "Data Access Name",
        //     type: "string",
        //     default_value: daName,
        //     mandatory: true,
        //     // validatorCallback: validateFunc,
        // })
		// fields.push({
        //     title: "DB Connection",
        //     type: "string",
        //     default_value: dataAccess[daName]['db_connection'],
        //     mandatory: true,
        //     // validatorCallback: validateFunc,
        // })
		// if(dataAccess[daName].hasOwnProperty('is_crud')){
		// 	fields.push({
		// 		title: "Is CRUD?",
		// 		type: "boolean",
		// 		default_value: dataAccess[daName]['is_crud'],
		// 		mandatory: true,
		// 		// validatorCallback: validateFunc,
		// 	})
		// }
		// if(dataAccess[daName].hasOwnProperty('is_crud_soft_delete')){
		// 	fields.push({
		// 		title: "Is CRUD Soft Delete?",
		// 		type: "boolean",
		// 		default_value: dataAccess[daName]['is_crud_soft_delete'],
		// 		mandatory: true,
		// 		// validatorCallback: validateFunc,
		// 	})
		// }
		// if(dataAccess[daName].hasOwnProperty('is_crud_soft_delete_token')){
		// 	fields.push({
		// 		title: "Is CRUD Soft Delete Token?",
		// 		type: "boolean",
		// 		default_value: dataAccess[daName]['is_crud_soft_delete_token'],
		// 		mandatory: true,
		// 		// validatorCallback: validateFunc,
		// 	})
		// }

		dispatch(setFields(fields))
	}

	return (
			<div className="node-title" onClick={setFormFields}>Setup</div>
	);
};

export default RenderSetup;
