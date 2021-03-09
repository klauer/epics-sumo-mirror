grep -i '^release' ../RELEASES.rst | tail -n 1 | sed -e 's/^[A-Za-z ]\+//'
