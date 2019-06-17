@echo off
setlocal

if [%1]==[] goto HELP
if [%1]==[--help] goto HELP
if [%2]==[] goto HELP
:: ****************************************************************************
:: Title :  xxxxx                                                        
:: 
:: Usage :  xxxxx                                                    
:: 
:: Args  :  xxxxx            
:: 
:: E.g.  :                                                               
:: 
:: Notes :                                                               
:: 
:: Requires: 
:: 
:: Returns:  
:: 
:: Author:   Zollty Tsou                                                      *
:: Version:  1.0.0                                                            *
:: Date:     03/26/2019                                                       *
:: Link:     zollty@163.com                                                   *
:: ****************************************************************************

echo ------------------------- starting clone -------------------------
call git clone --depth 1 --single-branch -b %2 %1 %3

goto EOF


:HELP
echo.
echo Usage: 
echo    input '{url} {branch} {rename(optinal)}' to clone the repo.
echo.
:EOF