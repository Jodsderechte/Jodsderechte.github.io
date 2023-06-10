#!/bin/bash

#!/bin/bash
jq -r '.hits[].id' < CrossOriginStuff/WeakAurasList.json > fetch-api-data-action/WaList_Converted.json
