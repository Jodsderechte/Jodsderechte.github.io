#!/bin/bash

#!/bin/bash

echo jq -r '.hits[].id' < CrossOriginStuff/WeakAurasList.json > WaList_Converted.json
