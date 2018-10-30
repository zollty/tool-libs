@echo off
setlocal
if [%1]==[] goto HELP
if [%1]==[--help] goto HELP
:: ****************************************************************************
:: Title :  find port                                                        
:: 
:: Usage :  port                                                    
:: 
:: Args  :  port: the port to search                      
:: 
:: E.g.  :  8080                                                             
:: 
:: Notes :                                                               
:: 
:: Requires: 
:: 
:: Returns:  
:: 
:: Author:   Zollty Tsou                                                      *
:: Version:  1.0.0                                                            *
:: Date:     03/05/2016                                                       *
:: Link:     https://github.com/zollty/tool-libs                              *
:: ****************************************************************************

set port=%1
netstat -a -n|findstr /r /c:".*:%port%.*"

goto EOF

:HELP
echo Usage: port
echo.

:EOF