import { useEffect } from "react";
import "./tree.scss";

const Tree = () => {
	const data = {
		ExampleCoreLib: {
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
		window.onclick = (e) => {
			document.getElementById(e.target.innerHTML).classList.toggle("hide");
			console.log(getObject(data, e.target.innerHTML))
		};
		renderTree(data, document.getElementById("tree"));
	}, []);

	const getObject = (obj, key) => {
		for (var prop in obj) {
			const sub = obj[prop];
			if(key == prop){
				console.log(sub)
			}
			if (typeof sub === "object") {
				getObject(sub, key);
			}
		}
	};

	const renderTree = (data, element) => {
		for (var key in data) {
			var newLI = document.createElement("li");
			if (
				typeof data[key] === "object" &&
				key !== "columns" &&
				key !== "classifiers"
			) {
				newLI.innerHTML = key;
				element.appendChild(newLI);
				var newUL = document.createElement("ul");
				newUL.setAttribute("id", key);
				element.appendChild(newUL);
				renderTree(data[key], newUL);
			}
		}
	};

	// const renderUL = (data) => {
	// 	if(typeof data == "object"){
	// 		return <ul>{render(data)}</ul>
	// 	}
	// }
	// const items = [];
	// const render = (data) => {
	// 	for (var key in data) {

	// 		if (typeof data[key] == 'object'){
	// 			items.push(
	// 				<li>
	// 					{key}
	// 					<ul>{render(data[key])}</ul>
	// 				</li>
	// 			)
	// 		}
	// 		// return (
	// 		// 	<>
	// 		// 	{
	// 		// 		typeof data[key] == 'object'?
	// 		// 		render(data[key]):null
	// 		// 	}
	// 		// 	</>
	// 		// );
	// 	};
	// };

	// const RenderRTree = () => {
	// 	render(data);
	// 	return items
	// };

	return (
		<div className="tree-root">
			<div className="tree">
				<ul id="tree"></ul>
			</div>
		</div>
	);
};

export default Tree;
