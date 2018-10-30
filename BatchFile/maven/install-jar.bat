@echo off
:: ****************************************************************************
:: Title :  install jar to maven local repo      
:: 
:: Usage :  自己修改call部分                                                                                                  
:: 
:: Notes :                                                               
:: 
:: Requires: Maven > mvn
:: 
:: Returns:  
:: 
:: Author:   Zollty Tsou                                                      *
:: Version:  1.0.0                                                            *
:: Date:     03/10/2016                                                       *
:: Link:     https://github.com/zollty/tool-libs                              *
:: ****************************************************************************

echo "=== start to install jars... ==="

call mvn install:install-file ^
-Dfile=D:/5temp/zollty-lib/api-base-1.1.jar ^
-DartifactId=api-base ^
-Dversion=1.1 ^
-DgroupId=org.jretty.commons ^
-Dpackaging=jar

echo "=== install jars finished ... ==="

pause




