import React from "react";

import { useDispatch } from "react-redux";
import { deleteFormField, addNewEntry } from "../slices/treeSlice";

import "./FunctionsTable.scss";
import HoverVisible from "../hoverVisible/HoverVisible";
import { useState } from "react";

const FunctionsTable = (props) => {
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
		props.value.map((func, index) => {
			return (
				<tr
					key={index}
					onMouseEnter={() => setVisible(true)}
					onMouseLeave={() => setVisible(false)}
					onMouseOver={() => setVisible(true)}
					className="tr"
				>
					<td key={`${props.fieldKey}.${index}.key`} className="td">
						<input
							type={"text"}
							id={`field-${props.fieldKey}.${index}.key`}
							className="form-input"
							defaultValue={func.key}
							required={true}
							placeholder="Name"
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.key`,
							})}
						/>
					</td>
					<td
						key={`${props.fieldKey}.${index}.return_type`}
						className="td"
					>
						<input
							type={"text"}
							id={`field-${props.fieldKey}.${index}.return_type`}
							className="form-input"
							defaultValue={func.return_type}
							required={true}
							placeholder="Return Type"
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.return_type`,
							})}
						/>
					</td>
					<td key={`${props.fieldKey}.${index}.result_to_dict`} className="td">
						<input
							type="checkbox"
							id={`${props.fieldKey}.${index}.result_to_dict`}
							name={"list" + props.fieldKey}
							value={func.result_to_dict}
							defaultChecked={func.result_to_dict}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.result_to_dict`,
							})}
						/>
					</td>
					<td
						className="td"
					>
						<input
							type="checkbox"
							id={`cache_toggle`}
							name={"list" + props.fieldKey}
							value={func.cache_invalidate}
							defaultChecked={func.cache_invalidate}
						/>
					</td>
					<td
						key={`${props.fieldKey}.${index}.cache_key`}
						className="td"
					>
						<input
							type={"text"}
							id={`field-${props.fieldKey}.${index}.cache_key`}
							className="form-input"
							defaultValue={func.cache_key}
							required={true}
							placeholder="Cache key"
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.cache_key`,
							})}
						/>
					</td>
					<td
						key={`${props.fieldKey}.${index}.cache_invalidate`}
						className="td"
					>
						<input
							type="checkbox"
							id={`${props.fieldKey}.${index}.cache_invalidate`}
							name={"list" + props.fieldKey}
							value={func.cache_invalidate}
							defaultChecked={func.cache_invalidate}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.cache_invalidate`,
							})}
						/>
					</td>

					<td className="td">
						<HoverVisible isVisible={visible}>
							<button
								className="column-del-btn"
								onClick={() =>
									onDeleteClick(`${props.fieldKey}.${index}`)
								}
							>
								<i className="fa-solid fa-trash-can"></i>
							</button>
						</HoverVisible>
					</td>
				</tr>
			);
		})
	);

	const RenderItems = (props) => {
		return (
			<>
				{props.value.length !== 0 ? (
					<table className="table">
						<thead>
							<tr className="tr">
								<th className="th">Name</th>
								<th className="th">Return Type</th>
								<th className="th">Result To Dict</th>
								<th className="th">Cache</th>
								<th className="th">Cache Key</th>
								<th className="th">Cache Invalidate</th>
							</tr>
						</thead>
						<tbody>{items}</tbody>
					</table>
				) : (
					""
				)}
			</>
		);
	};
	return (
		<div className="columns-root">
			<div className="columns-title-div">
				<div className="columns-title">Functions</div>
				<button
					className="column-add-btn"
					onClick={() => onAddClick(`${props.fieldKey}`)}
				>
					<i className="fa-solid fa-plus fa-xl"></i>
				</button>
			</div>

			<div>
				<RenderItems value={props.value} />
			</div>
		</div>
	);
};

FunctionsTable.defaultProps = {
	fieldKey: "",
	index: 1,
	onChange: () => {},
	title: "",
	value: [],
};

export default FunctionsTable;
