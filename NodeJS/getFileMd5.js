var fs = require('fs');
var crypto = require('crypto');

var path = 'D:/WindowsImageBackup/LAPTOP-RI69UHU9/Backup 2017-12-12 071326/bb65ae61-e88b-45bb-89a9-b3929e2d6ec1.vhdx';
var start = new Date().getTime();
var md5sum = crypto.createHash('md5');
var stream = fs.createReadStream(path);
stream.on('data', function (chunk) {
    md5sum.update(chunk);
});
stream.on('end', function () {
    str = md5sum.digest('hex').toUpperCase();
    console.log('文件:' + path + ',MD5签名为:' + str + '.耗时:' + (new Date().getTime() - start) / 1000.00 + "秒");
});

console.log('sssssssssssss')