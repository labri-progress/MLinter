#!/bin/bash

in_dev=false
all_rules=false
while getopts da flag
do
    case "${flag}" in
        d) in_dev=true;;
        a) all_rules=true;;
        *) echo "Invalid option: ${flag}";;
    esac
done

echo "Setting & Executing eslint..."
echo
cd output/tmp || return

echo "Setting eslint..."
cp ../../step_4_resources/package.json .
npm i > /dev/null 2>&1

if [ "$in_dev" == "true" ]; then
  cp ../../step_4_resources/dev.eslintrc .eslintrc
elif [ "$all_rules" == "true" ]; then
  cp ../../step_4_resources/all.eslintrc .eslintrc
else
  cp ../../step_4_resources/auto-fixable-and-one-liner.eslintrc .eslintrc
fi
echo "Setting eslint... done"
echo

while IFS=: read -r name clone_url; do
  echo "Executing eslint for $name..."
  ./node_modules/.bin/eslint --ext .js --no-color -f json -c .eslintrc -o "../result/linter/$name.json" "$name"
  echo "Executing eslint for $name... done"
  echo
done < "../result/repo_urls/dataset.txt"
echo "Setting & Executing eslint... done"

rm -f package.json package-lock.json
rm -rf node_modules
