#!/bin/bash
readarray -t  arr2 < <(git diff currLatest Latest --name-only)
for i in "${arr2[@]}"; do
    if [[ "${i}" == *"/"* ]]; then
        funName=$(dirname "$i")
        echo -e "serverless deploy function --function ${funName}\n"  >> deploy.sh
    fi
done

if [ -s "deploy.sh" ]; then
    echo "full"
else
    echo "EMPTY"
    echo -e "serverless deploy" >> deploy.sh
fi
