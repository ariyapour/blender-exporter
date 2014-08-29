#filename = "/home/ariyapour/git/blender-exporter/material.py"
#exec(compile(open(filename).read(), filename, 'exec'))
#bpy.data.materials['Material'].node_tree.nodes['Refraction BSDF'].inputs['Color'].links[0].from_node.name

import bpy
import json
import copy
import re

mainPath= "/home/ariyapour/git/blender-exporter"

#Adds brdf to shade function
def addToShade(fileName, initJson,currentNode):
    
    if initJson["body"][0]["body"]["body"][0]["argument"]["type"] == "CallExpression":
        fileName = fileName+ "_toShade.json"
    else:
        fileName = fileName+ ".json"
    addBSDFFile = open(mainPath+'/ast_files/'+ fileName,'r')
    addBSDF = json.load(addBSDFFile)
    
    if initJson["body"][0]["body"]["body"][0]["argument"]["type"] != "CallExpression":
        initJson["body"][0]["body"]["body"][0]["argument"] = addBSDF
    else:  
        objectAst = copy.deepcopy(initJson["body"][0]["body"]["body"][0]["argument"])
        initJson["body"][0]["body"]["body"][0]["argument"]["callee"] = {}
        initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["object"] = objectAst
        initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["type"] = "MemberExpression"
        initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["computed"] = False
        initJson["body"][0]["body"]["body"][0]["argument"]["arguments"]= addBSDF["arguments"]
        initJson["body"][0]["body"]["body"][0]["argument"]["callee"]["property"] = addBSDF["property"]
        initJson["body"][0]["body"]["body"][0]["argument"]["type"] = "CallExpression"    
        
    for input in currentNode.inputs :    
      if input.is_linked:
        if input.name == "Color":
          addBSDF["arguments"].pop(0)
          addBSDF["arguments"]. insert(0, {"type": "Identifier","name": currentNode.name.replace(" ", "")+input.name.replace(" ", "")})
    

def ifFunctionExists(name):
  for dic in initJson["body"]:
    if dic["id"]["name"] == name:
      return True
  return False

#adds a call function and adds the function declaration to the end
def addFunction_call(fileName,nextNode,currentInput, initJson):
   funcFile = open(mainPath+'/ast_files/' + fileName,'r')
   func = json.load(funcFile)
   
   func["functionCall"]["declarations"][0]["id"]["name"] =  nextNode.name.replace(".","").replace(" ", "")+currentInput.name.replace(" ", "")
   initJson["body"][0]["body"]["body"].insert(0,func["functionCall"])
   
   #change the arguments names in case we have multiple calls
   for argument in func["functionCall"]["declarations"][0]["init"]["arguments"]:
       if argument["type"]== "MemberExpression":
          argument["property"]["name"] = currentInput.links[0].from_node.name.replace(".","").replace(" ", "") + argument["property"]["name"] 
       else: 
           if argument["type"]== "CallExpression":
               argument["callee"]["object"]["name"] = currentInput.links[0].from_node.name.replace(".","").replace(" ", "") + argument["callee"]["object"]["name"]
           

   for dic in func["function"]:
     if not ifFunctionExists(dic["id"]["name"]): 
       initJson["body"].append(dic)



def writeShaderParameters(nextNode,currentNode):
        if currentNode.name != "Volume" and currentNode.name != "Displacement" :
          print (currentNode.name)
          ### we have to store these as shader parameters
          if not currentNode.links:
            if hasattr(currentNode.default_value, '__iter__'):
                ## Write the shader parameters ##############
              if currentNode.type == "RGBA" and currentNode.name == "Color":  
                shaderParameters.write("<float3 name=\""+ nextNode.name.replace(" ", "")+currentNode.name.replace(" ", "")+"\"> ")
                ## add the values
                for i in range(0,3) :
                  print (currentNode.default_value[i])
                  shaderParameters.write(str(currentNode.default_value[i])+ " " )
                shaderParameters.write("</float3>\n")
            else:
                print(currentNode.default_value)
                shaderParameters.write("<float name=\""+ nextNode.name.replace(" ", "")+currentNode.name.replace(" ", "")+"\"> " + str(currentNode.default_value) + "</float>\n")



def followLinks(node_in):
    for n_inputs in node_in.inputs:
        #Writing shader parameters
        writeShaderParameters(node_in,n_inputs)
    
                
        for node_links in n_inputs.links:
                                ##second node                          ##original node
            print("going to " + node_links.from_node.name + " from " + n_inputs.name)
            
            
            
#            if node_links.from_node.name == "Diffuse BSDF":
#              addToShade('diffuseAst.json', initJson,node_links.from_node)

              
              
              ##first we have to make a call with the parameter of the original node in left and call of the second node in right then add the second node to the end of javascriptcode
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
   

            #For voronoi texture the scale should be even and not more than 32 for now
            nodeName = re.search(r"Voronoi Texture*",node_links.from_node.name)
            if nodeName:
              if nodeName.group() == "Voronoi Texture":
                ##for voronoi texture for now we don't check the inputs!
                addFunction_call('voronoi.json',node_in,n_inputs,initJson)
            
            nodeName = re.search(r"ColorRamp*",node_links.from_node.name)
            if nodeName:
              if nodeName.group() == "ColorRamp":
                addFunction_call('colorRamp_linearInterpolation.json',node_in,n_inputs,initJson)
                for p in range(0,len(node_links.from_node.color_ramp.elements)-1):
                    shaderParameters.write("<float name=\"position"+ str(p+1) +"\"> " + str(node_links.from_node.color_ramp.elements[p].position) + "</float>\n")
                    shaderParameters.write("<float3 name=\"colorRamp"+ str(p+1) +"\"> " + str(node_links.from_node.color_ramp.elements[p].color[0]) + " " + str(node_links.from_node.color_ramp.elements[p].color[1]) + " " +str(node_links.from_node.color_ramp.elements[p].color[2]) + "</float3>\n")
                  
                  




            nodeName = re.search(r"Glossy BSDF* | Refraction BSDF* | Glass BSDF* | Diffuse BSDF*",node_links.from_node.name)
            if nodeName:
                if (nodeName.group() == "Glossy BSDF" or nodeName.group() == "Refraction BSDF" or nodeName.group() == "Glass BSDF" or nodeName.group() == "Diffuse BSDF"):
#             print("distribution: "+ str(node_links.from_node.distribution))
                  if (node_links.from_node.outputs[0].links[0].to_node.name != "Mix Shader"):
                      ##reflection
                    if node_links.from_node.name == "Glossy BSDF" :
                      addToShade('addReflect',initJson,node_links.from_node)
                      
                      ##Refraction
                    if node_links.from_node.name == "Refraction BSDF" :
                      addToShade('addRefract_toShade',initJson,node_links.from_node)  
     
                    if node_links.from_node.name == "Diffuse BSDF":
                      addToShade('addDiffuse.json', initJson,node_links.from_node)

                  


            nodeName = re.search(r"Mix Shader*",node_links.from_node.name)
            if nodeName:
                if nodeName.group() == "Mix Shader":
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[1].links[0].from_node.name == "Refraction BSDF"):
                    #if node_links.from_node.inputs[0].links[0].from_node.name == "Layer Weight":
                    ###add refract to shade()###########################################
                    addToShade('addRefract', initJson,node_links.from_node.inputs[1].links[0].from_node)
                    
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[1].links[0].from_node.name == "Diffuse BSDF"):
                    ###add diffuse to shade()###########################################
                    addToShade('addDiffuse', initJson,node_links.from_node.inputs[1].links[0].from_node)
                     
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[1].links[0].from_node.name == "Glossy BSDF"):
                    ###add reflect to shade()###########################################
                    addToShade('addReflect', initJson,node_links.from_node.inputs[1].links[0].from_node)  
                    
                    
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[2].links[0].from_node.name == "Refraction BSDF"):
                    #if node_links.from_node.inputs[0].links[0].from_node.name == "Layer Weight":
                    ###add refract to shade()###########################################
                    addToShade('addRefract', initJson,node_links.from_node.inputs[2].links[0].from_node)
                    
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[2].links[0].from_node.name == "Diffuse BSDF"):
                    ###add diffuse to shade()###########################################
                    addToShade('addDiffuse', initJson,node_links.from_node.inputs[2].links[0].from_node)
                     
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[2].links[0].from_node.name == "Glossy BSDF"):
                    ###add reflect to shade()###########################################
                    addToShade('addReflect', initJson,node_links.from_node.inputs[2].links[0].from_node)     
                    
                  if (node_links.from_node.inputs[0].is_linked and node_links.from_node.inputs[0].links[0].from_node.name == "Fresnel"):    
                    ###### add fresnel################################################
                    addFunction_call('fresnel.json',node_links.from_node,node_links.from_node.inputs[0],initJson)                
                
                
                
#               if (node_links.from_node.inputs[2].links[0].from_node.name == "Glossy BSDF"):
#                 ###add reflect to shade()###########################################
#                 addToShade('addReflect', initJson,node_links.from_node.inputs[2].links[0].from_node)


                  ###################################################################
                  

 
                
            if node_links.from_node.name == "Toon BSDF":
              print ("Component: "+node_links.from_node.component)
            if node_links.from_node.name == "Subsurface Scattering":
              print ("Component: "+node_links.from_node.falloff) 
              
              
              
            followLinks(node_links.from_node)


initFile = open(mainPath+'/ast_files/shaders.json', 'r')
shaderParameters = open(mainPath+'/ast_files/shader_parameters.txt', 'w')
shaderParameters.write("<data>\n")
initJson = json.load(initFile)
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
initFile.close()

