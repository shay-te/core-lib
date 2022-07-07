import React from 'react';
import Head from '@docusaurus/Head';
import Layout from "@theme/Layout";

import { store } from './../components/store/store';
import { Provider } from 'react-redux';
import {
    init,
    setStorageIndex,
} from "./../components/slices/treeSlice";
import { useDispatch } from "react-redux";
import { newCL } from './../newCoreLib';
import './generate.scss'
import { useHistory } from '@docusaurus/router';

const yaml = require('js-yaml');

function Generate() {
    const history = useHistory();
    const dispatch = useDispatch()
    const coreLibs = (JSON.parse(localStorage.getItem('core_libs')) === null ? [] : JSON.parse(localStorage.getItem('core_libs')))
    const recent_core_libs = [];
    if (coreLibs === null || coreLibs.length === 0) {
        recent_core_libs.push(
            <div key={'placeholder'}>
                No core-libs yet.
                Create a new core lib or upload an existing yaml.
            </div>
        )
    } else {
        recent_core_libs.push(
            coreLibs.map((coreLib, index) => {
                return (
                    <div className={`cl-btn`} onClick={() => navigateGenerator(coreLib, index)} key={`${coreLib.core_lib.name}-${index}`}>
                        {coreLib.core_lib.name}
                    </div>

                )
            })
        )
    }

    const addNew = (data) => {
        if(coreLibs.length >= 10){
            coreLibs.splice(0, 1);
            localStorage.setItem('core_libs', JSON.stringify(coreLibs));
        }
        navigateGenerator(data, coreLibs.length)
    }

    const navigateGenerator = (data, index) => {
        dispatch(setStorageIndex(index))
        dispatch(init(data));
        history.push('/generator')
    }

    const handleYamlInput = (files) => {
        if (files) {
            var reader = new FileReader();
            reader.readAsText(files[0], "UTF-8");
            reader.onload = function (evt) {
                const obj = yaml.load(evt.target.result)
                addNew(obj)
            }
            reader.onerror = function (evt) {
                alert('Some error occured')
            }
        }
    }

    return (
        <div className='generate-wrap'>
            <Layout>
                <Head>
                    <script src="https://kit.fontawesome.com/9ff5ab3bcf.js" crossorigin="anonymous"></script>
                </Head>
                <div className='generate-root'>
                    <div className='generate-divider'>
                        <div>
                            <h2>
                                Create
                            </h2>
                            <div className={`create-cl-btn button button--secondary button--lg `} onClick={() => addNew(newCL)}>
                                Create New
                            </div>
                        </div>
                        <div className='upload-root'>
                        <h2>
                            Upload
                        </h2>
                        <label className="custom-file-upload">
                            <input type={'file'} accept=".yaml, .yml" className='hide' onChange={(e) => handleYamlInput(e.target.files)} />
                            Yaml Upload
                        </label>
                    </div>
                        <div className='core-lib-list'>
                            <h2>
                                History:
                            </h2>
                            {recent_core_libs}
                        </div>
                    </div>
                </div>
            </Layout>
        </div>
    )
}

export default function Main() {
    return (
        <Provider store={store}>
            <Generate />
        </Provider>
    )
}