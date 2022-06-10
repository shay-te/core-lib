export const getBoolean = (value) => {
    if (typeof value === 'boolean') {
        return value;
    }
    if (value && value.trim().toLowerCase() === 'true') {
        return true;
    }
    return false;
}

export const isObject = (obj) => {
    return obj != null && obj.constructor.name === "Object"
}

export const download = (file, name) => {
    const a = document.createElement('a');
    const newFile = new Blob([file]);
    a.href = URL.createObjectURL(newFile);
    a.download = name
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

export const getENVValue = (envVar, yamlData) => {
    const CoreLibName = Object.keys(yamlData)[0]
    return yamlData[CoreLibName]["env"][envVar.split(":")[1].slice(0, -1)];
};

export const toSnakeCase = (str) => {
    return str && str.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g).map(x => x.toLowerCase()).join('_')
}

export const toCamelCase = (str) => {
    const newStr = str.toLowerCase().replace(/[^a-zA-Z0-9]+(.)/g, (n, chr) => chr.toUpperCase())
    return newStr.charAt(0).toUpperCase() + newStr.slice(1)
}

export const getValueAtPath = (obj, path) => {
    return path.reduce((key, val) => key && key[val] ? key[val] : '', obj);
}

export const setValueAtPath = (obj, path, value) => {
    const key = path.at(-1)
    const target = getValueAtPath(obj, path.slice(0, -1) )
    target[key] = value
    return obj
}