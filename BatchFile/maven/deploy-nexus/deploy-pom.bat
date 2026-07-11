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


echo "=== Start to deploy pom... ==="

set   releasesRepoId=diy-nexus-releases
set  releasesRepoUrl=http://192.168.20.157:8520/repository/maven-releases/

set  snapshotsRepoId=diy-nexus-snapshots
set snapshotsRepoUrl=http://192.168.20.157:8520/nexus/content/repositories/snapshots/

set base_dir=D:/__SYNC2/git/jretty-pom

:main
    rem 调用deployPom函数处理jar包
	call :deployPom jretty 21 org.jretty
    echo "=== deploy pom finished ... ==="
	pause


:: deploy file
:deployPom (artifactId, version, groupId)
	set COMMAND=deploy:deploy-file ^
	-DartifactId=%1 ^
	-Dversion=%2 ^
	-DgroupId=%3 ^
	-Dfile=%base_dir%/pom.xml ^
	-Dpackaging=pom
    setlocal enableDelayedExpansion
    echo(%2|findstr /r /c:".*SNAPSHOT$" >nul && (
      set COMMAND=%COMMAND% -DrepositoryId=%snapshotsRepoId% -Durl=%snapshotsRepoUrl%
    ) || (
      rem NOT FOUND
      set COMMAND=%COMMAND% -DrepositoryId=%releasesRepoId% -Durl=%releasesRepoUrl%
    )
    call D:\__SYNC1\Softwares\apache-maven-3.6.3\bin\mvn %COMMAND% --settings=D:\__SYNC0\00WORK\ide-config\settings.xml
	goto :eof
