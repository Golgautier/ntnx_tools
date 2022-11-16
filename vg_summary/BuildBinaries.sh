#!/bin/bash

echo "Binary creation for AOS_VG_List"

OS="linux windows darwin"
ARCH="arm64 amd64"

for OSTMP in $OS
do
    for ARCHTMP in $ARCH
    do
        echo "Building binary for $OSTMP ($ARCHTMP)"

        if [[ "$OSTMP" == "windows" ]]
        then
            GOOS=$OSTMP GOARCH=$ARCHTMP go build -o binary/AOS_VG_List.$OSTMP.$ARCHTMP.exe
        else
            GOOS=$OSTMP GOARCH=$ARCHTMP go build -o binary/AOS_VG_List.$OSTMP.$ARCHTMP
        fi
    done
done