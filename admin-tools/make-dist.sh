#!/bin/bash
PACKAGE=mathics3_module_pyicu

# FIXME put some of the below in a common routine
function finish {
  cd $mathics3_module_pyicu_owd
}

cd $(dirname ${BASH_SOURCE[0]})
mathics3_module_pyicu_owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-versions ; then
    exit $?
fi


cd ..
source pymathics/icu/version.py
echo $__version__

pyversion=3.13
if ! pyenv local $pyversion ; then
    exit $?
fi

pip wheel --wheel-dir=dist .
python -m build --sdist
finish
