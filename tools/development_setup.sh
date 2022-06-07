#!/bin/bash

kritaDir=~/.local/share/krita

thisModule=../src/
dukrifModule=../../DuKRIF/dukrif
OCOModule=../../../OCO/ocopy

# convert to absolute paths
thisModule=$(cd "$thisModule"; pwd)
kritaDir=$(cd "$kritaDir"; pwd)
dukrifModule=$(cd "$dukrifModule"; pwd)
OCOModule=$(cd "$OCOModule"; pwd)

# remove existing OCO if any
rm -r -f "$kritaDir/pykrita/OCO"
rm -f "$kritaDir/pykrita/OCO.desktop"

# Link desktop file and create the plugin dir
ln -s -t "$kritaDir/pykrita" "$thisModule/OCO.desktop"
mkdir "$kritaDir/pykrita/OCO"
mkdir "$kritaDir/pykrita/OCO/dukrif"
mkdir "$kritaDir/pykrita/OCO/ocopy"

# link plugin files
for file in $thisModule/OCO/*.*; do
    ln -s -t "$kritaDir/pykrita/OCO" "$file"
    echo "Linked $file"
done

# link DuKRIF
for file in $dukrifModule/*.py; do
    ln -s -t "$kritaDir/pykrita/OCO/dukrif" "$file"
    echo "Linked $file"
done

# link OCO
for file in $OCOModule/*.py; do
    ln -s -t "$kritaDir/pykrita/OCO/ocopy" "$file"
    echo "Linked $file"
done

echo "Done!"