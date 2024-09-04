#!/bin/bash -v
#-------------------------------------------------------------------------------
# Name        : clean.sh
# Description : Remove dirt files from the repository.
#
# Authors     : William A. Romero R.  <william.romero@umontpellier.fr>
#                                     <contact@waromero.com>
#
#-------------------------------------------------------------------------------
find . -name "\.DS_STORE*" -type f -delete -print
find . -name "\._.DS_Store" -type f -delete -print
find . -name "\._*" -type f -delete -print
find . -type d -name  "__pycache__" -exec rm -r {} +
find . -name "*~" -delete -type f -delete -print
echo "[clean] Done!"
