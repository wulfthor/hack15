#!/bin/bash

curl -s http://www.europeana.eu/api/v2/search.json?wskey=n3aquk8HA\&query="Caspar+David+Friedrich&qf=TYPE:IMAGE" | python -mjson.tool
