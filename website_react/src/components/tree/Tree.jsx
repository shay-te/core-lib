import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { getDataAccessList, YamlData } from "../utils/YamlData";
import {
	init
} from "./../slices/treeSlice";
import RenderCoreLibName from "./RenderCoreLibName";
import RenderDataAccess from "./RenderDataAccess";
import RenderDBConn from "./RenderDBConn";
import RenderSetup from "./RenderSetup";
import "./tree.scss";

const Tree = () => {

	return (	
		<div className="tree-root">
			<div className="tree">
				<RenderCoreLibName/>
				<RenderDataAccess />
				<RenderDBConn />
				<RenderSetup />
			</div>
		</div>
	);
};

export default Tree;
