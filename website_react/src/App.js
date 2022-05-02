import { useEffect } from 'react';
import './App.scss';
import Form from './components/form/Form';
import Tree from './components/tree/Tree';
import {
	init
} from "./components/slices/treeSlice";
import {useDispatch, useSelector} from "react-redux";
import { YamlData } from './components/utils/YamlData';

function App() {
	const clName = useSelector((state) => state.treeData.CoreLibName);
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch();

	const data = {
		ExampleCoreLib: {
			env: {
				USERDB_USER: "user",
				USERDB_PASSWORD: "password",
				USERDB_PORT: 5432,
				USERDB_DB: "userdb",
				USERDB_HOST: "localhost",
				SELLERDB_USER: "user",
				SELLERDB_PASSWORD: "password",
				SELLERDB_PORT: 5432,
				SELLERDB_DB: "sellerdb",
				SELLERDB_HOST: "localhost",
				MONGODB_USER: "user",
				MONGODB_PASSWORD: "password",
				MONGODB_PORT: 11211,
				MONGODB_DB: "mongo",
				MONGODB_HOST: "localhost",
				REDIS_HOST: "localhost",
				REDIS_PORT: 6379,
			},
			config: {
				data: {
					userdb: {
						log_queries: false,
						create_db: true,
						session: {
							pool_recycle: 3200,
							pool_pre_ping: false,
						},
						url: {
							protocol: "postgresql",
							username: "${oc.env:USERDB_USER}",
							password: "${oc.env:USERDB_PASSWORD}",
							host: "${oc.env:USERDB_HOST}",
							port: "${oc.env:USERDB_PORT}",
							file: "${oc.env:USERDB_DB}",
						},
					},
					sellerdb: {
						log_queries: false,
						create_db: true,
						session: {
							pool_recycle: 3200,
							pool_pre_ping: false,
						},
						url: {
							protocol: "postgresql",
							username: "${oc.env:SELLERDB_USER}",
							password: "${oc.env:SELLERDB_PASSWORD}",
							host: "${oc.env:SELLERDB_HOST}",
							port: "${oc.env:SELLERDB_PORT}",
							file: "${oc.env:SELLERDB_DB}",
						},
					},
					mongodb: {
						url: {
							protocol: "mongodb",
							username: "${oc.env:MONGODB_USER}",
							password: "${oc.env:MONGODB_PASSWORD}",
							host: "${oc.env:MONGODB_HOST}",
							port: "${oc.env:MONGODB_PORT}",
							file: "${oc.env:MONGODB_DB}",
						},
					},
				},
				cache: {
					cache_name: {
						type: "redis",
						url: {
							protocol: "redis",
							host: "${oc.env:REDIS_HOST}",
							port: "${oc.env:REDIS_PORT}",
						},
					},
				},
				jobs: {
					update_seller: {
						initial_delay: "0s",
						frequency: "",
						handler: {
							_target_:
								"example_core_lib.example_core_lib.jobs.update_seller.UpdateSeller",
						},
					},
				},
			},
			data_layers: {
				data: {
					userdb: {
						details: {
							db_connection: "userdb",
							columns: {
								name: {
									type: "VARCHAR",
									default: "",
								},
								active: {
									type: "BOOLEAN",
									default: false,
								},
							},
							is_soft_delete: true,
							is_soft_delete_token: true,
						},
						data: {
							db_connection: "userdb",
							columns: {
								address: {
									type: "VARCHAR",
									default: "",
								},
								contact: {
									type: "INTEGER",
									default: 0,
								},
							},
							is_soft_delete: true,
							is_soft_delete_token: false,
						},
						migrate: true,
					},
					sellerdb: {
						details: {
							db_connection: "sellerdb",
							columns: {
								name: {
									type: "VARCHAR",
									default: "",
								},
							},
							is_soft_delete: true,
							is_soft_delete_token: true,
						},
						data: {
							db_connection: "sellerdb",
							columns: {
								name: {
									type: "VARCHAR",
									default: "",
								},
								password: {
									type: "VARCHAR",
									default: "",
								},
							},
							is_soft_delete: false,
							is_soft_delete_token: false,
						},
						migrate: false,
					},
				},
				data_access: {
					DetailsDataAccess: {
						entity: "details",
						db_connection: "userdb",
						is_crud: true,
						is_crud_soft_delete: true,
						is_crud_soft_delete_token: true,
					},
					DataDataAccess: {
						entity: "data",
						db_connection: "userdb",
					},
					SellerDetailsDataAccess: {
						entity: "details",
						db_connection: "sellerdb",
					},
					SellerDataAccess: {
						entity: "data",
						db_connection: "sellerdb",
						is_crud: true,
					},
				},
			},
			setup: {
				author: "Jon Doe",
				author_email: "jon@doe.com",
				description: "Simple core lib project",
				url: "http://google.com",
				license: "APACHE_LICENSE_2",
				classifiers: [
					"Framework :: Flask",
					"Development Status :: 3 - Alpha",
					"Environment :: MacOS X",
					"Environment :: Win32 (MS Windows)",
					"Topic :: Software Development",
					"Topic :: Software Development :: Libraries",
				],
				version: "0.0.0.1",
			},
		},
	};

	useEffect(() => {
		dispatch(init(data))
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
			<Tree/>
			<Form onChange={onFieldChange}/>
		</div>
	);
}

export default App;
