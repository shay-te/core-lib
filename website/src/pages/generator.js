import React, {useEffect} from 'react';
import Head from '@docusaurus/Head';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useHistory } from '@docusaurus/router';
import Layout from "@theme/Layout";

import './generator.scss';
import Form from './../components/form/Form';
import {
    init,
	updateFields,
} from "./../components/slices/treeSlice";
import { useDispatch, Provider, useSelector } from "react-redux";
import { store } from './../components/store/store';
import 'react-reflex/styles.css'
import Link from '@docusaurus/Link';
import { Key } from '../utils/Key';
import DoubleMenu from '../components/doubleMenu/DoubleMenu';


function GeneratorElements() {
    const yaml = useSelector((state) => state.treeData.yaml);
    const dispatch = useDispatch();
    const history = useHistory();

    useEffect(() => {
        if(JSON.stringify(yaml) === '{}'){
            const recentCoreLib = JSON.parse(localStorage.getItem('recent_core_lib'))
            if(recentCoreLib){
                dispatch(init(recentCoreLib))
            } else {
                history.push('/generate')
            }
        }
    }, [])

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

function Generator() {
	const { siteConfig } = useDocusaurusContext();
	return (
		<Provider store={store}>
			<div className='generator-wrap'>
				<Layout>
					<Head>
						<script src="https://kit.fontawesome.com/9ff5ab3bcf.js" crossorigin="anonymous"></script>
					</Head>
					<GeneratorElements />
				</Layout>
			</div>
		</Provider>
	)
}

export default Generator;