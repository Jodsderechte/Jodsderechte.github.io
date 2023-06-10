#!/bin/bash

#!/bin/bash

jq -r '.hits[].id' < CrossOriginStuff/WeakAurasList.json > CrossOriginStuff/WaList_Converted.json
