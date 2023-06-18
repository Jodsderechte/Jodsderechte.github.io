#!/bin/bash

#!/bin/bash
jq -c '[.hits[].id]' < fetch-api-data-action/WeakAurasList.json > fetch-api-data-action/WaList_Converted.json
