#!/bin/bash

echo "Cloning all repositories & Cleaning..."
echo

cd output/tmp || return
while IFS=: read -r name clone_url; do
  echo "Cloning $clone_url from $name..."

  git clone "$clone_url" "$name" > /dev/null 2>&1
  cd "$name" || return
  git log -n 1 --pretty=format:"%H" > "../../result/commit_id/$name"
  echo "Cloning $clone_url from $name... done"

  echo "Removing npm & eslint stuffs from $name..."
  find . -name "package*.json" -type f -delete
  find . -name ".npmrc" -type f -delete
  find . -name ".nvmrc" -type f -delete
  find . -name ".eslint*" -type f -delete
  find . -name "*.min.js" -type f -delete
  rm -rf node_modules
  echo "Removing npm & eslint stuffs from $name... done"

  cd .. || return
  echo
done < "../result/repo_urls/dataset.txt"
echo "Cloning all repositories & Setting package.json... done"
