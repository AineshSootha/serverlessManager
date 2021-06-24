'use strict';

module.exports.thirdFun = async(event) => {
    return {
        statusCode: 200,
        body: JSON.stringify({
                message: 'This is the dev version of fun3',
                input: event,
            },
            null,
            2
        ),
    };
};