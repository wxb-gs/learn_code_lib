#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")"
echo "当前目录：$(pwd)"
git pull
git add .
git status
sleep 2s
git commit -m "update: $(date +"%Y-%m-%d %H:%M:%S")"
git push --set-upstream origin master
echo "执行完毕"
sleep 2s
