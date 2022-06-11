#!/bin/bash

outputDir=output

thisModule=../src/
dukrifModule=../../DuKRIF/dukrif
OCOModule=../../../OCO/ocopy

# convert to absolute paths
thisModule=$(cd "$thisModule"; pwd)
outputDir=$(cd "$outputDir"; pwd)
dukrifModule=$(cd "$dukrifModule"; pwd)
OCOModule=$(cd "$OCOModule"; pwd)

# remove existing OCO if any
rm -rf "$outputDir/OCO"
rm -f "$outputDir/OCO.desktop"

# Link desktop file and create the plugin dir
cp "$thisModule/OCO.desktop" "$outputDir/OCO.desktop"

# copy plugin files
cp -rf "$thisModule/OCO"  "$outputDir/OCO"
# copy DuKRIF
cp -rf "$dukrifModule"  "$outputDir/OCO/dukrif"
# copy OCO
cp -rf "$OCOModule"  "$outputDir/OCO/ocopy"

echo "Done!"