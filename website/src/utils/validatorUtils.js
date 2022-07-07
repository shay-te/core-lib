export const isPascalCase = (string) => {
    return /^[A-Z][A-Za-z0-9]*$/.test(string.trim())
}

export const isSnakeCase = (string) => {
    return /^[a-z]+(?:_[a-z0-9]+)*$/.test(string.trim())
}

export const isSnakeCaseCapital = (string) => {
    return /^[A-Z]+(?:_[A-Z0-9]+)*$/.test(string.trim())
}

export const isBoolean = (string) => {
    return (String(string.trim()) === 'true' || String(string.trim()) === 'false')
}

export const isNumber = (string) => {
    return !isNaN(string)
}

export const isNotNull = (string) => {
    return string.trim().length > 0
}

export const isEmail = (string) => {
    return /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(string.trim())
}

export const isURL = (string) => {
    let url;

    try {
        url = new URL(string.trim());
    } catch (_) {
        return false;
    }

    return url.protocol === "http:" || url.protocol === "https:";
}

export const isTimeFrame = (string) => {
    const timeparse = require('timeparse');
    const trimmed_string = string.trim();
    if(trimmed_string === 'boot' || trimmed_string === 'startup'){
        return true;
    }
    return (timeparse(trimmed_string) !== 0 || trimmed_string === '0s')

    
}