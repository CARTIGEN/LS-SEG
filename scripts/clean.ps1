# PowerShell Script: clean-up.ps1
#-------------------------------------------------------------------------------
# Name        : clean.ps1
# Description : Remove dirt files from the repository.
#
# Authors     : William A. Romero R.  <william.romero@umontpellier.fr>
#                                     <contact@waromero.com>
#
#-------------------------------------------------------------------------------

Get-ChildItem -Recurse -Filter ".DS_STORE*" -File | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Output "Deleted: $($_.FullName)"
}

Get-ChildItem -Recurse -Filter "._.DS_Store" -File | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Output "Deleted: $($_.FullName)"
}

Get-ChildItem -Recurse -Filter "._*" -File | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Output "Deleted: $($_.FullName)"
}

Get-ChildItem -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    Write-Output "Deleted directory: $($_.FullName)"
}

Get-ChildItem -Recurse -Filter "*~" -File | ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Output "Deleted: $($_.FullName)"
}

Write-Output "[clean] Done!"