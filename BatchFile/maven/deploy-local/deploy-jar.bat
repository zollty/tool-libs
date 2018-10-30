@echo off

echo "=== start to deploy jar... ==="

:: 也可以直接 deploy:deploy-file
call mvn org.apache.maven.plugins:maven-deploy-plugin:3.0.0-M1:deploy-file -X ^
    -Durl=file:///D:/0sync-local/git/repository ^
    -DrepositoryId=git-repo ^
    -Dfile=./apollo-client-0.10.3-SNAPSHOT.jar ^
    -DpomFile=./apollo-client-0.10.3-SNAPSHOT.pom ^
    -Dsources=./apollo-client-0.10.3-SNAPSHOT-sources.jar
::    -Djavadoc=./apollo-client-0.10.3-SNAPSHOT-javadoc.jar

echo "=== deploy jar finished ... ==="

pause
