@echo off
:: ****************************************************************************
:: Title :  deploy jar to maven repositories                                                      
::                                                                            
:: Usage :  根据需要自己修改 1.设置各变量; 2.在main函数里面添加相关参数.
::                                                                            
:: Notes :  
::   1. 参数pomFile、sources、javadoc为可选，但是建议都有
::   2. 区分SNAPSHOT版本和RELEASE版本,repository和url不一样
::   3. 参见官方文档：http://maven.apache.org/plugins/maven-deploy-plugin/deploy-file-mojo.html                                              
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

:main
    rem 调用deployJar函数处理jar包
	call :deployJar api-base 1.0 org.zollty
    call :deployJar jretty-log 1.2-SNAPSHOT org.jretty
    echo "=== deploy jars finished ... ==="
	pause


:: deploy file
:deployJar (artifactId, version, groupId)
	set COMMAND=deploy:deploy-file ^
	-DartifactId=%1 ^
	-Dversion=%2 ^
	-DgroupId=%3 ^
	-Dfile=%base_dir%/%1-%2.jar ^
	-DpomFile=%base_dir%/pom.xml ^
	-Dsources=%base_dir%/%1-%2-sources.jar ^
	-javadoc=%base_dir%/%1-%2-javadoc.jar
    setlocal enableDelayedExpansion
    echo(%2|findstr /r /c:".*SNAPSHOT$" >nul && (
      set COMMAND=%COMMAND% -DrepositoryId=%snapshotsRepoId% -Durl=%snapshotsRepoUrl%
    ) || (
      rem NOT FOUND
      set COMMAND=%COMMAND% -DrepositoryId=%releasesRepoId% -Durl=%releasesRepoUrl%
    )
    call mvn %COMMAND%
	goto :eof
