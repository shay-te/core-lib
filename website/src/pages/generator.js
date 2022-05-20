import React from 'react';
import Head from '@docusaurus/Head';

import './generator.scss';
import Form from './../components/form/Form';
import Tree from './../components/tree/Tree';
import {
	init,
	updateFields
} from "./../components/slices/treeSlice";
import { useDispatch, useSelector } from "react-redux";
import { testInput } from './../testInput';
import { useEffect } from 'react';
import { store } from './../components/store/store';
import { Provider } from 'react-redux';

import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from "@theme/Layout";
import clsx from "clsx";

function Generator() {
	const { siteConfig } = useDocusaurusContext();
	const yamlData = useSelector((state) => state.treeData.yaml);
	const dispatch = useDispatch()

	useEffect(() => {
		if (JSON.stringify(yamlData) === '{}') {
			dispatch(init(testInput))
		}
		else {
			dispatch(init(yamlData))
		}

	}, [])

	const onFieldChange = (field, e) => {
		if (field.key) {
			dispatch(updateFields({ path: field.key, value: e.target.value, env: field.env, addOrRemove: e.target.checked }))
		}
	}
	return (
		<div className='app-root'>
			<Tree key={'tree'} />
			<Form onChange={onFieldChange} />
		</div>
	);
}

function App() {
	const { siteConfig } = useDocusaurusContext();
	return (
		<Provider store={store}>
			<Layout>
				<Head>
					<script src="https://kit.fontawesome.com/9ff5ab3bcf.js" crossorigin="anonymous"></script>
				</Head>
				<Generator />
			</Layout>
		</Provider>
	)
}

export default App;