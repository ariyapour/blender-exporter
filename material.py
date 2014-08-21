#filename = "/home/ariyapour/git/blender-exporter/material.py"
#exec(compile(open(filename).read(), filename, 'exec'))
#bpy.data.materials['Material'].node_tree.nodes['Refraction BSDF'].inputs['Color'].links[0].from_node.name

import bpy
import json
import copy

mainPath= "/home/ariyapour/git/blender-exporter"


def followLinks(node_in):
    for n_inputs in node_in.inputs:
        if n_inputs.name != "Volume" and n_inputs.name != "Displacement" :
          print (n_inputs.name)
          ### we have to store these as shader parameters
          if not n_inputs.links:
            if hasattr(n_inputs.default_value, '__iter__'):
                ## Write the shader parameters ###############################################
              if n_inputs.type == "RGBA" and n_inputs.name == "Color":  
                shaderParameters.write("<float3 name=\""+ node_in.name.replace(" ", "")+n_inputs.name.replace(" ", "")+"> ")
                ## add the values
                for i in range(0,3) :
                  print (n_inputs.default_value[i])
                  shaderParameters.write(str(n_inputs.default_value[i])+ " " )
                shaderParameters.write("</float3>\n")
            else:
                print(n_inputs.default_value)
                shaderParameters.write("<float name=\""+ node_in.name.replace(" ", "")+n_inputs.name.replace(" ", "")+"> " + str(n_inputs.default_value) + "</float>\n")
                
                
                
                
        for node_links in n_inputs.links:
            print("going to " + node_links.from_node.name + " from " + n_inputs.name)
            if node_links.from_node.name == "Diffuse BSDF":
              diffuseFile = open(mainPath+'/ast_files/diffuseAst.json','r')
              diffuseJson = json.load(diffuseFile)
              initJson["body"][0]["body"]["body"][0]["argument"] = diffuseJson
            if node_links.from_node.name == "Math":
              print ("operation: "+node_links.from_node.operation + "\nClamp:" + str(node_links.from_node.use_clamp))
            if node_links.from_node.name == "Vector Math":
              print ("operation: "+node_links.from_node.operation)
            if node_links.from_node.name == "Mapping":
              print ("Location: "+str(node_links.from_node.location) + "\nRotation: " + str(node_links.from_node.rotation) + "\nScale: " + str(node_links.from_node.scale) + "\nMax: " + str(node_links.from_node.max) + "\nMin: " + str(node_links.from_node.min))
            if node_links.from_node.name == "Bump":
              print ("Inverr: "+str(node_links.from_node.invert))
            if node_links.from_node.name == "Normal Map":
              print ("Space: "+node_links.from_node.space)
              if node_links.from_node.space == "TANGENT":
                print("uv_map: "+ str(node_links.from_node.uv_map))
            if node_links.from_node.name == "Normal Map":
              print ("Space: "+node_links.from_node.space)   
   

            if node_links.from_node.name == "Voronoi Texture":
              voronoiFile = open(mainPath+'/ast_files/voronoi.json','r')
              voronoi = json.load(voronoiFile)
              initJson["body"][0]["body"]["body"].insert(0,voronoi["voronoiCall"])
              initJson["body"].append(voronoi["voronoiFunction"])




            if (node_links.from_node.name == "Glossy BSDF" or node_links.from_node.name == "Refraction BSDF" or node_links.from_node.name == "Glass BSDF"):
              print("distribution: "+ str(node_links.from_node.distribution))
              if (node_links.from_node.outputs[0].links[0].to_node.name != "Mix Shader"):
                if node_links.from_node.name == "Glossy BSDF" :
                  glossyBSDFFile = open(mainPath+'/ast_files/glossyBSDFAst.json','r')
                  glossyBSDF = json.load(glossyBSDFFile)
                  initJson["body"][0]["body"]["body"][0]["argument"] = glossyBSDF



            if node_links.from_node.name == "Mix Shader":
              if (node_links.from_node.inputs[1].links[0].from_node.name == "Refraction BSDF") and (node_links.from_node.inputs[2].links[0].from_node.name == "Glossy BSDF"):
                if node_links.from_node.inputs[0].links[0].from_node.name == "Layer Weight":

                  ###add refract to shade()###########################################
                  addRefractfile = open(mainPath+'/ast_files/addRefract_test.json','r')
                  addRefract = json.load(addRefractfile)
                  objectAst = copy.deepcopy(initJson["body"][0]["body"]["body"][0]["argument"])
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"] = {}
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["object"] = objectAst
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["type"] = "MemberExpression"
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["computed"] = False
                  initJson["body"][0]["body"]["body"][0]["argument"]["arguments"]= addRefract["arguments"]
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["property"] = addRefract["property"]
                  initJson["body"][0]["body"]["body"][0]["argument"]["type"] = "CallExpression"
                  ###################################################################

                  ###add reflect to shade()###########################################
                  addReflectfile = open(mainPath+'/ast_files/addReflect_test.json','r')
                  addReflect = json.load(addReflectfile)
                  objectAst = copy.deepcopy(initJson["body"][0]["body"]["body"][0]["argument"])
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"] = {}
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["object"] = objectAst
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["type"] = "MemberExpression"
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["computed"] = False
                  initJson["body"][0]["body"]["body"][0]["argument"]["arguments"]= addReflect["arguments"]
                  initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["property"] = addReflect["property"]
                  initJson["body"][0]["body"]["body"][0]["argument"]["type"] = "CallExpression"
                  ###################################################################
                  
                  ####### add fresnel################################################
                  fresnelFile = open(mainPath+'/ast_files/fresnelAst_call.json','r')
                  fresnel = json.load(fresnelFile)
                  initJson["body"].append(fresnel["body"][0])
                  initJson["body"].append(fresnel["body"][1])
                  initJson["body"][0]["body"]["body"].insert(0,fresnel["functionCall"][0])
                  initJson["body"][0]["body"]["body"].insert(0,fresnel["functionCall"][1])
 
                
            if node_links.from_node.name == "Toon BSDF":
              print ("Component: "+node_links.from_node.component)
            if node_links.from_node.name == "Subsurface Scattering":
              print ("Component: "+node_links.from_node.falloff) 
              
              
              
            followLinks(node_links.from_node)


jsonFinal = open(mainPath+'/ast_files/shaders.json', 'r')
shaderParameters = open(mainPath+'/ast_files/shader_parameters.txt', 'w')
shaderParameters.write("<data>\n")
initJson = json.load(jsonFinal)
for mat in bpy.data.materials:
    print("Traversing " + mat.name)
    for mat_node in mat.node_tree.nodes:
        if mat_node.type == 'OUTPUT_MATERIAL':
            # we start at the material output node
            print("Starting at " + mat_node.name) 
            followLinks(mat_node)
final = open(mainPath+'/ast_files/finalAst.json','w')
json.dump(initJson,final)
shaderParameters.write("<\data>")
shaderParameters.close()
final.close()
jsonFinal.close()

