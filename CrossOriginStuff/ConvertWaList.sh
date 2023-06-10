#!/bin/bash

#!/bin/bash
echo jq -r '.hits[].id' < WeakAurasList.json > WaList_Converted.json
