#!/bin/sh
git clean -fdx
cd repos/$1
git checkout -- .
git clean -fdx
