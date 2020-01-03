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

set /a min=%1*60
shutdown -s -t %min%

goto EOF

:HELP
echo Usage: min
echo.

:EOF

