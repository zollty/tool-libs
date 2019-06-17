@echo off
setlocal

echo.
call java -version
echo.
SET JAVA_HOME=D:\C\Program Files\Java\jdk1.7.0_80
echo ------------------------- maven info -------------------------------
call mvn -v

if [%1]==[] goto HELP
if [%1]==[--help] goto HELP
if [%1]==[install] goto INSTALL
if [%1]==[deploy] goto DEPLOY
if [%1]==[testdp] goto TESTDP
goto HELP
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
:: Date:     02/28/2018                                                       *
:: Link:     zollty@163.com                                                   *
:: ****************************************************************************

:: add "-Pjretty-doc" to generate java docs

:INSTALL
echo ------------------------- starting to install -------------------------
cd %2
call mvn clean install -Pjretty-release

goto EOF

:DEPLOY
echo ------------------------- starting to deploy -------------------------
cd %2
call mvn clean deploy -Pjretty-release -Plocal-deploy

goto EOF

:TESTDP
echo ------------------------- starting to deploy -------------------------
cd %2
call mvn clean deploy -Ptest-deploy -Pjretty-release

goto EOF

:HELP
echo.
echo Usage: 
echo    input 'deploy ${PATH}' to deploy to local repo.
echo    input 'install ${PATH}' to execute install.
echo.
:EOF