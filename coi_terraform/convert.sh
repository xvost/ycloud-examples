#!/bin/bash
cat ./docker-compose.yaml | sed -E ':a;N;$!ba;s/\r{0,1}\n/\\n/g' | sed "s/\"/'/g" > ./tmp
echo -En "variable \"docker-compose\" {
  default = \"`cat ./tmp`\"
}
" > ./docker-compose.tf && rm ./tmp