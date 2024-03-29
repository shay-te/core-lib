import { isEmail, isNotNull, isURL } from "../utils/validatorUtils"

export const setupFields = (yamlData) => {
    const fields = []
    const CoreLibName = Object.keys(yamlData)[0]
    const keyPrefix = CoreLibName + '.setup'
    const setup = yamlData[CoreLibName]['setup']
    fields.push(
        {
            title: "Project url",
            type: "string",
            default_value: '',
            value: setup.url,
            mandatory: false,
            key: keyPrefix + '.url',
            toolTipTitle: "Should start with https or http (Optional)",
            validatorCallback: isURL,
        },
        {
            title: "Project Description",
            type: "string",
            default_value: '',
            value: setup.description,
            mandatory: true,
            key: keyPrefix + '.description',
            validatorCallback: isNotNull,
        },
        {
            title: "Project version",
            type: "string",
            default_value: '',
            value: setup.version,
            mandatory: true,
            key: keyPrefix + '.version',
            validatorCallback: isNotNull,
        },
        {
            title: "License Type",
            type: "enum",
            default_value: 'MIT',
            value: setup.license,
            mandatory: true,
            options: [
                'MIT',
                'APACHE_LICENSE_2',
                'MOZILLA_PUBLIC_LICENSE_2',
            ],
            key: keyPrefix + '.license',
        },
        {
            title: "Your Full Name",
            type: "string",
            default_value: '',
            value: setup.author,
            mandatory: true,
            key: keyPrefix + '.author',
            validatorCallback: isNotNull,
        },
        {
            title: "Your Email",
            type: "string",
            default_value: '',
            value: setup.author_email,
            mandatory: true,
            key: keyPrefix + '.author_email',
            validatorCallback: isEmail,
        },
        {
            title: 'Select classifiers',
            type: 'list',
            value: setup.classifiers,
            mandatory: true,
            multiple_selection: true,
            options: [
                'Development Status :: 3 - Alpha',
                'Development Status :: 4 - Beta',
                'Development Status :: 5 - Production/Stable',
                'Environment :: MacOS X',
                'Environment :: Win32 (MS Windows)',
                'Framework :: Django :: 4.0',
                'Framework :: Flask',
                'Framework :: Jupyter',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python :: 3.7',
                'Topic :: Software Development',
                'Topic :: Software Development :: Libraries',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Typing :: Typed',
            ],
            key: keyPrefix + '.classifiers',
        },
    )
    return fields
}