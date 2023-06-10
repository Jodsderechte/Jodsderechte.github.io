#!/bin/bash

#!/bin/bash
echo jq -r '.hits[].id' < CrossOriginStuff/WeakAurasList.json > fetch-api-data-action/WaList_Converted.json
