//var generate = require('./Generate_code.js')
//generate.generate()

exports.generate = function ()
{
var escodegen = require('escodegen')
var json = require('../ast_files/finalAst.json')
var fs = require('fs')
fs.writeFile("./code.js",escodegen.generate(json))
return;
}
