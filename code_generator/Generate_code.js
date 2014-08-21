//var generate = require('./Generate_code.js')
//generate.generate()

exports.generate = function ()
{
var escodegen = require('escodegen')
var json = require('/home/ariyapour/Dropbox/Master Thesis_CG/blender-2.70a-linux-glibc211-x86_64/ast_files/finalAst.json')
var fs = require('fs')
fs.writeFile("./code.js",escodegen.generate(json))
return;
}
