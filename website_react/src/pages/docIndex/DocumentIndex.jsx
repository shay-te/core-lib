import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import './DocumentIndex.scss'

const DocumentIndex = () => {
	const [markdown, setMarkdown] = useState("");

	const readmePath = require(`./doc_index.md`);
	useEffect(() => {
		(async () => {
			const response = await fetch(readmePath);
			const content = await response.text();
			setMarkdown(content);
		  })();
	}, []);
	return <div className="doc-index-root">
		<ReactMarkdown
				children={markdown}
			/>
	</div>;
};

export default DocumentIndex
