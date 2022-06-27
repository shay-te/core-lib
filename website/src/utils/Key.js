export class Key {

    toString(keyArray){
        console.log(keyArray.join('.'))
        return keyArray.join('.')
    }
    
    parse(key){
        const keySplit = key.split('.');
        let isBoolean = false;
        if(keySplit[0] === 'true' || keySplit[0] === 'false'){
            isBoolean = true
        }
        return { isBoolean, key }
    }
}