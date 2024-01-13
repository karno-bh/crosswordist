#!/usr/bin/bash


function clean {
    rm -rf *.o *.so
}

INCLUDE_PATH="/usr/include/python3.10/"

function compile {
    for CFILE in *.c
    do
        # echo "$CFILE"
        # extension="${CFILE##*.}"
        filename="${CFILE%.*}"
        # echo "$filename -- $extension"
        # echo $INCLUDE_PATH
        echo "Compiling $CFILE"
        gcc -fPIC "$CFILE" -shared -o "$filename.so" $(python3-config --cflags --ldflags)
    done
}

case "$1" in
    clean)
        clean
    ;;
    build)
        clean
        compile
    ;;
    *)
        echo "Unknown target"
    ;;
esac