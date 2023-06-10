#!/bin/bash

#!/bin/bash
jq -r '.hits[].id' < WeakAurasList.json > WaList_Converted.json
