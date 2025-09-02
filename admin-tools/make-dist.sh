#!/bin/bash
PACKAGE=Mathics3-Module-pyicu

# FIXME put some of the below in a common routine
function finish {
  cd $mathics_pyicu_owd
}

cd $(dirname ${BASH_SOURCE[0]})
mathics_pyicu_owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-versions ; then
    exit $?
fi


cd ..
source pymathics/language/version.py
echo $__version__

if ! pyenv local $pyversion ; then
    exit $?
fi

python setup.py bdist_wheel --universal
mv -v dist/pymathics_module_pyicu-${__version__}-{py2.,}py3-none-any.whl
python ./setup.py sdist
finish
