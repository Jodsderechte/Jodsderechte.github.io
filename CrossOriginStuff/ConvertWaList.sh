#!/bin/bash

#!/bin/bash
curl -s 'https://data.wago.io/search/es?q=User%3A%22Jodsderechte%22&mode=wow&page=0&sort=' | jq -cr '"content=\([.hits[].id])"' > fetch-api-data-action/WaList_Converted.json
