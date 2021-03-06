#!/bin/bash

ID=`python -mjson.tool .ask/ask-states.json | python -c 'import sys, json; print json.load(sys.stdin)["profiles"]["default"]["skillId"]'`
mkdir -p skill-package/interactionModels/custom/
ask smapi get-interaction-model -s "$ID" --stage development -l en-US > skill-package/interactionModels/custom/en-US.json
cat skill-package/interactionModels/custom/en-US.json

