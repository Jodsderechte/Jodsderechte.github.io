#!/bin/bash

#!/bin/bash
mkdir -p CrossOriginStuff
jq -r '.hits[].id' < CrossOriginStuff/WeakAurasList.json > CrossOriginStuff/WaList_Converted.json
