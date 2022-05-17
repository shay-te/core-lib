import InputDropDown from "../inputs/InputDropDown";
import InputString from "../inputs/InputString";

import { useDispatch } from "react-redux";
import {
	deleteFormField,
	addNewEntry,
} from "../slices/treeSlice";

import "./ColumnsTable.scss";
import HoverVisible from "../hoverVisible/HoverVisible";
import { useState } from "react";

const ColumnsTable = (props) => {
	const dispatch = useDispatch();
	const [visible, setVisible] = useState(false);

	const onDeleteClick = (path) => {
		dispatch(deleteFormField(path));
	};

	const onAddClick = (path) => {
		dispatch(addNewEntry(path));
	};

	const items = [];
	items.push(
		props.value.map((column, index) => {
			return (
				<tr
					key={index}
					onMouseEnter={() => setVisible(true)}
					onMouseLeave={() => setVisible(false)}
					onMouseOver={() => setVisible(true)}
				>
					<td key={`${props.fieldKey}.${index}.key`}>
						<InputString
							key={`${props.fieldKey}.${index}.key`}
							mandatory={true}
							value={column.key}
							default_value={""}
							fieldKey={`${props.fieldKey}.${index}.key`}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.key`,
							})}
						/>
					</td>
					<td key={`${props.fieldKey}.${index}.type`}>
						<InputDropDown
							key={`${props.fieldKey}.${index}.type`}
							mandatory={true}
							value={column.type}
							default_value={""}
							fieldKey={`${props.fieldKey}.${index}.type`}
							options={["VARCHAR", "BOOLEAN", "INTEGER"]}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.type`,
							})}
						/>
					</td>
					<td key={`${props.fieldKey}.${index}.default`}>
						<InputString
							key={`${props.fieldKey}.${index}.default`}
							mandatory={true}
							value={column.default}
							default_value={""}
							fieldKey={`${props.fieldKey}.${index}.default`}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.default`,
							})}
						/>
					</td>
					<HoverVisible isVisible={visible}>
						<td>
							<button
								className="column-del-btn"
								onClick={() =>
									onDeleteClick(`${props.fieldKey}.${index}`)
								}
							>
								<i className="fa-solid fa-trash-can"></i>
							</button>
						</td>
					</HoverVisible>
				</tr>
			);
		})
	);
	return (
		<div className="columns-root">
			<label className="input-label">Columns</label>
			<div>
				<table>
					<tr>
						<th>Name</th>
						<th>Type</th>
						<th>Default</th>
					</tr>
					<tbody>{items}</tbody>
				</table>
			</div>
			<button
				className="column-add-btn"
				onClick={() => onAddClick(`${props.fieldKey}`)}
			>
				<i className="fa-solid fa-plus fa-2xl"></i>
			</button>
		</div>
	);
};

export default ColumnsTable;
