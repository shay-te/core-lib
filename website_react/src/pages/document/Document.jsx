import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import gfm from 'remark-gfm'
import CodeBlock from "../../components/codeBlock/CodeBlock";

import "./Document.scss";
import { useParams } from "react-router-dom";

const Document = () => {
	const [markdown, setMarkdown] = useState("");

	const params = useParams()
	const readmePath = require(`./../../docs/${params.doc}.md`);
	useEffect(() => {
		(async () => {
			const response = await fetch(readmePath);
			const content = await response.text();
			setMarkdown(content);
		  })();
	}, []);

	return (
		<div className="document-root">
			<ReactMarkdown
				children={markdown}
				remarkPlugins={[gfm]}
				components={CodeBlock}
			/>
		</div>
	);
};

export default Document;
