#!/bin/bash

#!/bin/bash

echo jq -r '.hits[].id' < CrossOriginStuff/WeakAurasList.json > CrossOriginStuff/WaList_Converted.json
