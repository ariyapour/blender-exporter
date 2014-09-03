//var x = require('./Generate_code.js')
//generate.generate()

exports.generate = function ()
{
	var escodegen = require('escodegen')
	var json = require('/home/ariyapour/git/blender-exporter/ast_files/finalAst.json')
	var fs = require('fs')
	fs.writeFile("./code.js",escodegen.generate(json,{hexadecimal: false}))
	return;
}
