#!/bin/bash

echo "Setting folders structure..."

[ -d output ] && rm -rf output

mkdir -p output/result/repo_urls
mkdir -p output/result/commit_id
mkdir -p output/tmp

echo "Setting folders structure... done"
