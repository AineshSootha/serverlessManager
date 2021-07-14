#!/bin/bash
#readarray -t  arrDeleted < <(git diff Latest currLatest  --name-only --diff-filter=D)
readarray -t  arrAdded < <(git diff Latest currLatest --name-only --diff-filter=A)
readarray -t  arrModded< <(git diff Latest currLatest --name-only --diff-filter=M)

if [ ${#arrAdded[@]} -eq 0 ]; then
    echo "No new functions detected"
else
    for i in "${arrAdded[@]}"; do
        funName=$(dirname "$i")
        sls deploy -c "$funName/serverless.yml"
    done
fi
for i in "${arrModded[@]}"; do
        funName=$(dirname "$i")
        sls deploy -c "$funName/serverless.yml"
done
