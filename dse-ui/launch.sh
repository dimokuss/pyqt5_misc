#!/bin/bash

# This is essentially a hard coded launch_something.sh

export THIS_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
$THIS_DIR/dselib/dse.py $@
