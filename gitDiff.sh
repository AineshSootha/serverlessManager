#!/bin/bash
readarray -t  arr2 < <(git diff currLatest Latest --name-only)
delVar=0
for i in "${arr2[@]}"; do
    if [[ "${i}" == *"/"* ]]; then
        if [ ! -f "$i" ]; then
            delVar=1
            break
        fi
    fi
done
if [ "$delVar" == 1 ]; then
    echo -e "serverless deploy" >> deploy.sh
    exit 0
else
    for i in "${arr2[@]}"; do
        if [[ "${i}" == *"/"* ]]; then
            funName=$(dirname "$i")
            echo -e "serverless deploy function --function ${funName}\n"  >> deploy.sh
        fi
    done
fi

if [ -s "deploy.sh" ]; then
    echo "deploy.sh created"
else
    echo -e "serverless deploy" >> deploy.sh
fi
