bl_info = {
   "name": "Forci Change Name Texture",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (2, 80, 0),
   "location": "View3D > Tool",
   "description": "Change material name for all objects in the scene based on Principled BSDF texture name, removing .png extension and numeric suffixes",
   "category": "FORCI STUFF",
}

import bpy
import re

class ForciChangeNameTextureOperator(bpy.types.Operator):
   """Change material name for all objects in the scene based on texture name used in shader nodes, 
      removing .png extension and numeric suffixes, including custom 'Neo Yakuza Shader' nodes"""
   bl_idname = "forcica.change_name_texture"
   bl_label = "Change Material Name"

   def execute(self, context):
      # Expression régulière pour détecter .png suivi ou non d'un suffixe numérique comme .001
      regex = re.compile(r"\.png(\.\d+)?$", re.IGNORECASE)
   
      for obj in bpy.context.scene.objects:
         if obj.type == 'MESH' and obj.data.materials:
               for material in obj.data.materials:
                  if material.use_nodes:
                     for node in material.node_tree.nodes:
                           # Vérifie si le nœud est un BSDF_PRINCIPLED ou un 'Neo Yakuza Shader'
                           if node.type == 'BSDF_PRINCIPLED' or (node.bl_idname == 'ShaderNodeGroup' and "Neo Yakuza Shader" in node.node_tree.name) or (node.bl_idname == 'ShaderNodeGroup' and "Yakuza Shader" in node.node_tree.name):
                              base_color_input = None
                              if node.type == 'BSDF_PRINCIPLED':
                                 base_color_input = node.inputs['Base Color']
                              elif node.bl_idname == 'ShaderNodeGroup':
                                 base_color_input = node.inputs['texture_diffuse']  # Nom d'entrée supposé pour le nœud custom

                              if base_color_input and base_color_input.is_linked:
                                 linked_node = base_color_input.links[0].from_node
                                 if linked_node.type == 'TEX_IMAGE':
                                       texture_name = linked_node.image.name
                                       # Retire l'extension .png et tout suffixe numérique
                                       texture_name = regex.sub('', texture_name)
                                       material.name = texture_name
                                       self.report({'INFO'}, f"Material '{material.name}' renamed based on texture name")
                                       break  # Nous avons trouvé un nœud de texture valide, pas besoin de continuer
      return {'FINISHED'}

class ForciChangeNameTexturePanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Change Name Texture"
   bl_idname = "MATERIAL_PT_forci_change_name_texture"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'
   
   def draw(self, context):
      layout = self.layout
      layout.operator(ForciChangeNameTextureOperator.bl_idname)

def register():
   bpy.utils.register_class(ForciChangeNameTextureOperator)
   bpy.utils.register_class(ForciChangeNameTexturePanel)

def unregister():
   bpy.utils.unregister_class(ForciChangeNameTextureOperator)
   bpy.utils.unregister_class(ForciChangeNameTexturePanel)

if __name__ == "__main__":
   register()
