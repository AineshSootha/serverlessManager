'use strict';

module.exports.pyTest = async(event) => {
    return {
        statusCode: 200,
        body: JSON.stringify({
                message: 'This is the testing function for the manager',
                input: event,
            },
            null,
            2
        ),
    };
};