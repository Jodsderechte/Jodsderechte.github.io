#!/bin/bash

#!/bin/bash
jq -r '[.hits[].id]' < Data/WeakAurasList.json > fetch-api-data-action/WaList_Converted.json
