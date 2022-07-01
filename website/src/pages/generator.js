import React from 'react';
import Head from '@docusaurus/Head';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from "@theme/Layout";

import './generator.scss';
import Form from './../components/form/Form';
import {
	updateFields
} from "./../components/slices/treeSlice";
import { useDispatch, Provider } from "react-redux";
import { store } from './../components/store/store';
import 'react-reflex/styles.css'
import Link from '@docusaurus/Link';
import { Key } from '../utils/Key';
import DoubleMenu from '../components/doubleMenu/DoubleMenu';

function Generator() {
	const dispatch = useDispatch()
	const onFieldChange = (field, e) => {
        const key = new Key()
        let isBool = false
        if (e.target.id){
            const data = key.parse(e.target.id)
            isBool = data['isBoolean']
        }
		if (field.key) {
			dispatch(updateFields({ path: field.key, value: e.target.value.trim(), env: field.env, addOrRemove: e.target.checked, isBool: isBool }))
		}
	}
	return (
		<>
			<div className='close-generator-btn'>
				<Link to='/generate'>
					Close
				</Link>
			</div>
			<div className='app-root' key={'app-root'}>
				<DoubleMenu key={'tree'} />
				<Form onChange={onFieldChange} />
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