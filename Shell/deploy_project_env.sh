#!/bin/bash
# 环境一键部署脚本，检查参数是否齐全，产生交互补全部署所需参数
# $1: 环境的Id
# $2：环境全称，例如(myalibaba.hz, login.alibaba, extaccountservice)
# $3：项目CRID（如果用已有TAR包地址部署，可以传入none）
# $4：环境类型（'FUNC','AUTO','PERF'）
# $5：TAR包地址
export PATH=$HOME/env_script:$PATH
export BASE="$HOME/env_script"
SCRIPT_SVN_PATH=""
MYDATE=`date +%Y-%m-%d_%H:%M:%S`
ENV_NAME=$1
CRID=$2
ENV_TYPE=$3
TAR_ADDRESS=$4
NEED_RESTORE=$5
check_url=$6
check_text=$7

source /etc/profile

# 检查应用名
if [ "x$ENV_NAME" = "x" ]; then
    echo -n -e "\e[0;32;1menv_name should not be empty\e[0m"
    exit 1
fi

# 检查项目CRID
if [ "x$CRID" = "x" ]; then
        echo -n -e "\e[0;32;1mproject CRID should not be empty\e[0m"
    exit 1
fi

# 检查配置项类型
if [ "x$ENV_TYPE" = "x" ]; then
        ENV_TYPE="FUNC"
fi

#项目环境部署，必要参数：$ENV_NAME $CRID。默认拿最新的TAR包部署，否则拉分支编译部署
#$BASE/env_deploy_flow.sh $ENV_NAME $CRID $ENV_TYPE $TAR_ADDRESS $NEED_RESTORE

log_info(){
    echo "[INFO] $1"
}

log_exit(){
    echo "[ERROR] $1"
    exit 1
}

kill_ws() {
    log_info "Kill All Web Service"
    #killall -9 java >>/dev/null 2>&1
    ps ux | grep java | awk '{print $2}' | xargs kill -9 >> /dev/null 2>&1
}


check_start() {
        local check_url=$1
	local check_text=$2
        log_info "start check $ENV_NAME with url: $check_url"
        local count=0
        while true
        do
        	((count++))
                [[ $count -gt 10 ]] && log_exit "fail to check app with url: $check_url" 
                log_info "try $count times"
                local content=`curl -s -m 20 $check_url`
                #echo "$content"
                #[  ${#content} -le 0 ] && continue 
                [[ "$content" =~ $check_text ]] && break;
                sleep 3
        done
        log_info "check ok!!!"
}

start_env(){

    kill_ws

    log_info "Start $ENV_NAME"
    cd /home/$USER
    wget http://package.switch.aliyun.com:8088/$TAR_ADDRESS
    echo "deploying war..."
    [ -d jetty9 ] || cp -r /usr/install/jetty9 ./ 
    [ -d jetty9/webapps ] &&   rm -rf jetty9/webapps/*.war
    mv *.war jetty9/webapps

    cd jetty9/bin/
    #nohup sh jetty.sh start &>/dev/null &
    nohup ./jetty.sh start &>/dev/null &

#    sleep 5
    check_start $check_url $check_text
}


start_env
exit 0
