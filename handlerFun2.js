'use strict';

module.exports.secondFun = async(event) => {
    return {
        statusCode: 200,
        body: JSON.stringify({
                message: 'This is the dev version of fun2',
                input: event,
            },
            null,
            2
        ),
    };
};