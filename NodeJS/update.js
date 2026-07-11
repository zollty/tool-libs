const path = require('path')
const fs = require('fs')
var os = require('os')
var cloneFile = require('./utils.js')

const rootPath = path.resolve(__dirname, '../')

console.log(rootPath);


// var mesm = fs.createWriteStream(__dirname + '/dist/zollty-util.default.js')
// var mdes = fs.createWriteStream(__dirname + '/dist/zollty-util.esm.js')
var mesm = fs.createWriteStream(path.resolve(rootPath + '/dist', 'zollty-util.default.js'))
var mdes = fs.createWriteStream(path.resolve(rootPath + '/dist', 'zollty-util.esm.js'))
const gg = []

let folderList = fs.readdirSync(path.resolve(rootPath, 'src'))
folderList.forEach((item, i) => {

    var sstats = fs.statSync(path.resolve(rootPath + '/src', item));

    if (sstats && sstats.isDirectory()) {
        let subFolder = fs.readdirSync(path.resolve(rootPath + '/src', item))
        subFolder.forEach((ff, j) => {
            let attr = ff.substring(0, ff.lastIndexOf('.'));
            gg.push(attr)
            mesm.write('import ' + attr + ' from \'./' + attr + '.js\';' + os.EOL);
            mdes.write('export { default as ' + attr + ' } from \'./' + attr + '.js\';' + os.EOL);
        })
    }

    fs.stat(path.resolve(rootPath + '/src', item), function (err, stat) {
        if (stat && stat.isDirectory()) {
            console.log(' ' + i + ' \033[36m' + item + '/\033[39m');
            var out = fs.createWriteStream(path.resolve(rootPath + '/dist', item + '.default.js'))
            var mdr = fs.createWriteStream(path.resolve(rootPath + '/dist', item + '.js'))

            let subFolder = fs.readdirSync(path.resolve(rootPath + '/src', item))
            const tg = [];
            subFolder.forEach((ff, j) => {
                let attr = ff.substring(0, ff.lastIndexOf('.'));
                console.log(' ' + j + ' \033[35m' + attr + '\033[39m');
                tg.push(attr)
                out.write('import ' + attr + ' from \'./' + attr + '.js\';' + os.EOL);
                mdr.write('export { default as ' + attr + ' } from \'./' + attr + '.js\';' + os.EOL);
                // cloneFile(__dirname + '/src/' + item + '/' + ff, __dirname + '/dist/' + ff);
                cloneFile(path.resolve(rootPath + '/src/' + item, ff), path.resolve(rootPath + '/dist', ff));
            })
            out.write(os.EOL)
            out.write('export default {' + os.EOL)
            for (let index = 0; index < tg.length; index++) {
                console.log(tg[index]);
                out.write('  ' + tg[index] + ',' + os.EOL)
            }
            out.write('}')
            mdr.write('export { default } from \'./' + item + '.default.js' + '\';' + os.EOL)
        } else {
            console.log(' ' + i + ' \033[32m' + item + '\033[39m');
            // cloneFile(__dirname + '/src/' + item, __dirname + '/dist/' + item);
            cloneFile(path.resolve(rootPath + '/src', item), path.resolve(rootPath + '/dist', item));
        }
    });
    console.log(i + ': ' + item)
})

mesm.write(os.EOL)
mesm.write('export default {' + os.EOL)
for (let index = 0; index < gg.length; index++) {
    mesm.write('  ' + gg[index] + ',' + os.EOL)
}
mesm.write('}')
mdes.write('export { default } from \'./zollty-util.default.js\';' + os.EOL)

// cloneFile(__dirname + '/dist/zollty-util.default.js', __dirname + '/dist/zollty.js');
cloneFile(path.resolve(rootPath + '/dist', 'zollty-util.default.js'), path.resolve(rootPath + '/dist', 'zollty.js'));

// function test(filename) {
//     console.log(filename)
// }

// folderList.map(filename => test(filename))
console.log('-----------------------------------');
// cloneFile('./tmp/a.js', './a.js');