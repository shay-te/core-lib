import React from "react";

import HoverVisible from "../hoverVisible/HoverVisible";
import { useState } from "react";

const ColumnsTable = (props) => {
	const [visible, setVisible] = useState(false);

	const items = [];
	items.push(
		props.value.map((column, index) => {
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
							defaultValue={column.key}
							required={true}
							placeholder="Column Name"
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.key`,
							})}
						/>
					</td>
					<td key={`${props.fieldKey}.${index}.type`} className="td">
						<select
							id={`${props.fieldKey}.${index}.type`}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.type`,
							})}
							value={column.type}
						>
							<option value="VARCHAR">VARCHAR</option>
							<option value="BOOLEAN">BOOLEAN</option>
							<option value="INTEGER">INTEGER</option>
						</select>
					</td>
					<td
						key={`${props.fieldKey}.${index}.default`}
						className="td"
					>
						<input
							type={"text"}
							id={`field-${props.fieldKey}.${index}.default`}
							className="form-input"
							defaultValue={column.default}
							required={true}
							placeholder="Column Default Value"
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.default`,
							})}
						/>
					</td>
					<td
						key={`${props.fieldKey}.${index}.nullable`}
						className="td"
					>
						<input
							type="checkbox"
							id={`${props.fieldKey}.${index}.nullable`}
							name={"list" + props.fieldKey}
							value={column.nullable}
							defaultChecked={column.nullable}
							onChange={props.onChange.bind(this, {
								key: `${props.fieldKey}.${index}.nullable`,
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

	const RenderItems = (props) => {
		return (
			<>
				{props.value.length !== 0 ? (
					<table className="table">
						<thead>
							<tr className="tr">
								<th className="th">Name</th>
								<th className="th">Type</th>
								<th className="th">Default</th>
								<th className="th">Nullable</th>
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
	return <RenderItems value={props.value} />;
};

ColumnsTable.defaultProps = {
	fieldKey: "",
	index: 1,
	onChange: ()=> {},
	onDeleteClick: ()=> {},
	title: "",
	value: [],
}

export default ColumnsTable;
