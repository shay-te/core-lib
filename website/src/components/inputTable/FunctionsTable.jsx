import React from "react";

import HoverVisible from "../hoverVisible/HoverVisible";
import { useState } from "react";

const FunctionsTable = (props) => {
	const [visible, setVisible] = useState(false);
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
						key={`${props.fieldKey}.${index}.result_to_dict`}
						className="td"
					>
						<input
							key={`${props.fieldKey}.${index}.result_to_dict`}
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
						key={`${props.fieldKey}.${index}.cache_key`}
						className="td"
					>
						<input
							key={`${props.fieldKey}.${index}.cache_key`}
							type={"text"}
							id={`field-${props.fieldKey}.${index}.cache_key`}
							className="form-input"
							value={func.cache_key}
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
								onClick={props.onDeleteClick.bind(
									this,
									`${props.fieldKey}.${index}`
								)}
							>
								<i className="fa-solid fa-trash-can"></i>
							</button>
						</HoverVisible>
					</td>
				</tr>
			);
		})
	);
	let render = [];
	if (props.value.length !== 0) {
		render.push(
			<table className="table">
				<thead>
					<tr className="tr">
						<th className="th">Name</th>
						<th className="th">Result To Dict</th>
						<th className="th">Cache Key</th>
						<th className="th">Cache Invalidate</th>
					</tr>
				</thead>
				<tbody>{items}</tbody>
			</table>
		);
	}
	return <>{render}</>;
};

FunctionsTable.defaultProps = {
	fieldKey: "",
	index: 1,
	onChange: () => {},
	onDeleteClick: () => {},
	title: "",
	value: [],
};

export default FunctionsTable;
