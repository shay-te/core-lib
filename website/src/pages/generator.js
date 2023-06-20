import React, {useEffect} from 'react';
import { Link, useNavigate } from 'react-router-dom';

import './generator.scss';
import Form from './../components/form/Form';
import {
    init,
	updateFields,
    setList,
    setFields,
} from "./../components/slices/treeSlice";
import { useDispatch, Provider, useSelector } from "react-redux";
import { store } from './../components/store/store';
import 'react-reflex/styles.css'
import { Key } from '../utils/Key';
import DoubleMenu from './../components/DoubleMenu/DoubleMenu';


function GeneratorElements() {
    const yaml = useSelector((state) => state.treeData.yaml);
    const dispatch = useDispatch();
    const navigate = useNavigate();

    useEffect(() => {
        if(JSON.stringify(yaml) === '{}'){
            const recentCoreLib = JSON.parse(localStorage.getItem('recent_core_lib'))
            if(recentCoreLib){
                dispatch(init(recentCoreLib))
            } else {
                navigate('/generate')
            }
        }
        dispatch(setList('core_lib'));
        dispatch(setFields({ title: "Core-Lib", path: "name" }));
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
				<Link to='/'>
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
	return (
		<Provider store={store}>
            <div>
                <div className='generator-wrap'>
                    <GeneratorElements />
                </div>
            </div>
			
		</Provider>
	)
}

export default Generator;