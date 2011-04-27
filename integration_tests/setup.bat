#!/usr/bin/sh
pushd ..
export PYTHONPATH=$(pwd -W)
popd
echo PYTHONPATH=$PYTHONPATH
