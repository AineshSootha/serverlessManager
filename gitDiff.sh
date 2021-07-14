#!/bin/bash
readarray -t  arrDeleted < <(git diff Latest currLatest  --name-only --diff-filter=D)
readarray -t  arrAdded < <(git diff Latest currLatest --name-only --diff-filter=A)
readarray -t  arrModded< <(git diff Latest currLatest --name-only --diff-filter=M)

for i in "${arrDeleted[@]}"; do
    if [[ "${i}" == *"/"* ]]; then
        funName=$(dirname "$i")
        slsmanager -l "$AWS_ACCESS_KEY_ID" "$AWS_SECRET_ACCESS_KEY" "$AWS_DEFAULT_REGION" -d "$funName"
    fi
done
if [ ${#arrAdded[@]} -eq 0 ]; then
    echo "No new functions detected"
else
    for i in "${arrAdded[@]}"; do
        funName=$(dirname "$i")
        slsmanager -i "$AWS_ACCESS_KEY_ID" "$AWS_SECRET_ACCESS_KEY" "$AWS_DEFAULT_REGION" "$funName"
    done
    echo -e "serverless deploy\nslsmanager -u\nserverless deploy" >> deploy.sh
    echo "deploy.sh successfully created"
    exit 0
fi
for i in "${arrModded[@]}"; do
        if [[ "${i}" == *"/"* ]]; then
            funName=$(dirname "$i")
            echo -e "serverless deploy function --function ${funName}\n"  >> deploy.sh
        fi
done
if [ ${#arrAdded[@]} -eq 0 ]; then
    echo "No functions modified"
    echo -e "echo "No functions to deploy"" >> deploy.sh
fi
