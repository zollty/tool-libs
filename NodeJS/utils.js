const fs = require('fs')

function cloneFile(src, dst) {
    var rs = fs.createReadStream(src);
    var ws = fs.createWriteStream(dst);
    rs.on('data', function (chunk) {
        if (ws.write(chunk) === false) { //ws.write()  判断数据流是否已经写入目标了
            rs.pause();
        }
    });
    rs.on('end', function () {
        ws.end();
    });
    ws.on('drain', function () {
        rs.resume(); //从新启动读取数据流
    });
}

module.exports = cloneFile;