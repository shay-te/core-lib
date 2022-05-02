import { useDispatch, useSelector } from "react-redux";
import { hideContents } from "../utils/commonUtils";

const RenderBranch = (props) => {
	const dispatch = useDispatch()
    const dataAccess = useSelector((state) => state.treeData.dataAccess);
	const CoreLibName = useSelector((state) => state.treeData.CoreLibName);
	const setup = useSelector((state) => state.treeData.setup);
	const dbConnections = useSelector((state) => state.treeData.dbConnections);
	const entities = useSelector((state) => state.treeData.entities);


    const RenderChildNodes = () => {
		return props.data.map((key) => {
            console.log(key)
			return <div className="node-child" key={key.name} onClick={() => props.fields(key.name, CoreLibName, dbConnections, dataAccess)}>{key.name}</div>;
		})
	}

    return (
        <div className="node-title" onClick={(e) => hideContents(e)}>{props.name}
        {
            props.data ? <RenderChildNodes/> : ''
        }
        </div>
);
}

export default RenderBranch