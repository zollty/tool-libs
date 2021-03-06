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

call mvn deploy:deploy-file -N -X ^
    -Durl=file:///D:/0sync-local/git/repository ^
    -DrepositoryId=git-repo ^
    -Dfile=./pom.xml ^
    -DpomFile=./pom.xml ^
    -Dpackaging=pom

echo "=== deploy pom finished ... ==="

pause
