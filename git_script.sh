#!/bin/bash

echo "Enter commit message:"
read commit_message

git pull
git add -A
git commit -a -m "$commit_message"
