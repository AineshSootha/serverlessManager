'use strict';

module.exports.firstFun = async(event) => {
    return {
        statusCode: 200,
        body: JSON.stringify({
                message: 'This is the dev version of fun1',
                input: event,
            },
            null,
            2
        ),
    };
};