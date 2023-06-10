#!/bin/bash

#!/bin/bash
jq -r '[.hits[].id]' < fetch-api-data-action/WeakAurasList.json > fetch-api-data-action/WaList_Converted.json
