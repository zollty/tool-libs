@echo off
:: ****************************************************************************
:: Title :  deploy jar to maven repositories                                                      
::                                                                            
:: Usage :  根据需要自己修改                                                                      
::                                                                            
:: Notes :                      
::   1. 参数pomFile、sources、javadoc为可选，但是建议都有
::   2. 区分SNAPSHOT版本和RELEASE版本,repository和url不一样
::   3. 参见官方文档：http://maven.apache.org/plugins/maven-deploy-plugin/deploy-file-mojo.html
::   4. 建议使用 deploy-jar-func-version.bat ，更加方便。                                                
::                                                                 
:: Requires: Maven > mvn                                                       
::                                                                            
:: Returns:  
::                                                                            *
:: Author:   Zollty Tsou                                                      *
:: Version:  1.0.0                                                            *
:: Date:     03/05/2016                                                       *
:: Link:     https://github.com/zollty/tool-libs                              *
:: ****************************************************************************

echo "=== Start to deploy jars... ==="

set   releasesRepoId=pre-nexus-releases
set  releasesRepoUrl=http://10.2.10.22:8081/nexus/content/repositories/releases/

set  snapshotsRepoId=pre-nexus-snapshots
set snapshotsRepoUrl=http://10.2.10.22:8081/nexus/content/repositories/snapshots/

set base_dir=C:/Users/zollty/lib

call mvn deploy:deploy-file ^
-DartifactId=api-base ^
-Dversion=1.1 ^
-DgroupId=org.zollty ^
-Dfile=%base_dir%/api-base-1.1.jar ^
-DpomFile=%base_dir%/pom.xml ^
-Dsources=%base_dir%/api-base-1.1-sources.jar ^
-Djavadoc=%base_dir%/api-base-1.1-javadoc.jar ^
-DrepositoryId=%releasesRepoId% -Durl=%releasesRepoUrl%

call mvn deploy:deploy-file ^
-DartifactId=jretty-log ^
-Dversion=1.2-SNAPSHOT ^
-DgroupId=org.jretty ^
-Dfile=C:/Users/zollty/jretty-log-1.2-SNAPSHOT.jar ^
-DpomFile=%base_dir%/pom.xml ^
-Dsources=%base_dir%/jretty-log-1.2-SNAPSHOT-sources.jar ^
-Djavadoc=%base_dir%/jretty-log-1.2-SNAPSHOT-javadoc.jar ^
-DrepositoryId=%snapshotsRepoId% -Durl=%snapshotsRepoUrl%


echo "=== deploy jars finished ... ==="

pause
