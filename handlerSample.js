'use strict';

module.exports.sampleFun = async(event) => {
    return {
        statusCode: 200,
        body: JSON.stringify({
                message: 'This is an example Lambda handler',
                input: event,
            },
            null,
            2
        ),
    };
};