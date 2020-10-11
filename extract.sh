#!/bin/sh
for file in ./*_results; do
    echo "$(basename "$file")"
    egrep -c "
done
