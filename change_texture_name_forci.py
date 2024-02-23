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
import re  # Importe le module pour les expressions régulières

class ForciChangeNameTextureOperator(bpy.types.Operator):
   """Change material name for all objects in the scene based on Principled BSDF texture name, removing .png extension and numeric suffixes"""
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
                           if node.type == 'BSDF_PRINCIPLED':
                              base_color_input = node.inputs['Base Color']
                              if base_color_input.is_linked:
                                 linked_node = base_color_input.links[0].from_node
                                 if linked_node.type == 'TEX_IMAGE':
                                       texture_name = linked_node.image.name
                                       # Utilise l'expression régulière pour retirer .png et tout suffixe numérique
                                       texture_name = regex.sub('', texture_name)
                                       material.name = texture_name
                                       break # Stop after finding the first valid texture to rename the material.
      self.report({'INFO'}, "Material names updated (without .png extension and numeric suffixes) for all objects in the scene")
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
