import React from 'react';
import Head from '@docusaurus/Head';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from "@theme/Layout";

import './generator.scss';
import Form from './../components/form/Form';
import Tree from './../components/tree/Tree';
import {
	updateFields
} from "./../components/slices/treeSlice";
import { useDispatch } from "react-redux";
import { store } from './../components/store/store';
import { Provider } from 'react-redux';

import {
	ReflexContainer,
	ReflexSplitter,
	ReflexElement
} from 'react-reflex'
import 'react-reflex/styles.css'
import Link from '@docusaurus/Link';

function Generator() {
	const dispatch = useDispatch()
	const onFieldChange = (field, e) => {
        let isBool = false
        const idArr = e.target.id.split('.')
        if(idArr[0] === 'true' || idArr[0] === 'false'){
            isBool = true
        }
		if (field.key) {
			dispatch(updateFields({ path: field.key, value: e.target.value, env: field.env, addOrRemove: e.target.checked, isBool: isBool }))
		}
	}
	return (
		<>
			<div className='close-generator-btn'>
				<Link to='/generate'>
					<i className="fa-solid fa-xmark"></i>
				</Link>
			</div>
			<div className='app-root' key={'app-root'}>
				<ReflexContainer orientation="vertical">
					<ReflexElement className="left-pane custom-scrollbar" minSize={250} size={300}>
						<Tree key={'tree'} />
					</ReflexElement>
					<ReflexSplitter />
					<ReflexElement className="right-pane custom-scrollbar" minSize={200}>
						<Form onChange={onFieldChange} />
					</ReflexElement>
				</ReflexContainer>
			</div>
		</>

	);
}

function App() {
	const { siteConfig } = useDocusaurusContext();
	return (
		<Provider store={store}>
			<div className='generator-wrap'>
				<Layout>
					<Head>
						<script src="https://kit.fontawesome.com/9ff5ab3bcf.js" crossorigin="anonymous"></script>
					</Head>
					<Generator />
				</Layout>
			</div>
		</Provider>
	)
}

export default App;