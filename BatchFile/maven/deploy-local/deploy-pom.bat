@echo off
:: ****************************************************************************
:: 语法如下：
:: 
:: mvn install:install-file 
:: -Dfile=[your file] -DgroupId=[xxxx] -DartifactId=[xxxx] -Dversion=[xxxx] 
:: -Dpackaging=[pom|jar|other]
:: 
:: mvn deploy:deploy-file -Dfile=[your file] -DgroupId=[xxxx] -DartifactId=[xxxx] 
:: -Dversion=[xxxx] -Dpackaging=[pom|jar|other] -DrepositoryId=[id] -Durl=[repo url]
:: 
:: Author:   Zollty Tsou                                                      *
:: Version:  1.0.0                                                            *
:: Date:     02/28/2018                                                       *
:: Link:     zollty@163.com                                                   *
:: ****************************************************************************
echo "=== start to deploy pom... ==="

call mvn org.apache.maven.plugins:maven-deploy-plugin:3.0.0-M1:deploy-file -X ^
    -Durl=file:///D:/0sync-local/git/repository ^
    -DrepositoryId=git-repo ^
    -Dfile=./apollo-0.10.3-SNAPSHOT.pom ^
    -DpomFile=./apollo-0.10.3-SNAPSHOT.pom ^
    -Dpackaging=pom

echo "=== deploy pom finished ... ==="

pause
