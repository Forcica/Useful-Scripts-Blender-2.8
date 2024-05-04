bl_info = {
   "name": "Forci Yakuza Shader Texture Handler",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (2, 80, 0),
   "location": "View3D > Tool",
   "description": "Handle Yakuza Shader Textures",
   "category": "FORCI STUFF",
}

import bpy
import os
import shutil

class ForciYakuzaTextureHandler(bpy.types.Operator):
   """Handle Yakuza Shader Textures"""
   bl_idname = "object.forci_yakuza_texture_handler"
   bl_label = "Handle Yakuza Shader Textures"

   @classmethod
   def poll(cls, context):
      return context.active_object is not None

   def execute(self, context):
      source_folder = bpy.context.scene.forci_yakuza_texture_props.source_folder
      destination_folder = bpy.context.scene.forci_yakuza_texture_props.destination_folder

      if not os.path.exists(destination_folder):
         os.makedirs(destination_folder)

      # Dictionary to hold base image names and their new paths to avoid duplicates
      processed_textures = {}

      for material in bpy.data.materials:
         if material.use_nodes:
               for node in material.node_tree.nodes:
                  if node.type == 'TEX_IMAGE' and node.image and '_d' in node.image.name:
                     base_image_name = os.path.splitext(node.image.name)[0]
                     if base_image_name.endswith('_d') and base_image_name not in processed_textures:
                           new_path = self.process_texture(node, source_folder, destination_folder, base_image_name)
                           if new_path:
                              processed_textures[base_image_name] = new_path

      # Go through the nodes again to assign the new images
      for material in bpy.data.materials:
         if material.use_nodes:
               for node in material.node_tree.nodes:
                  if node.type == 'TEX_IMAGE' and node.image:
                     base_image_name = os.path.splitext(node.image.name)[0]
                     if base_image_name in processed_textures:
                           node.image = bpy.data.images.load(processed_textures[base_image_name])

      self.report({'INFO'}, "Yakuza Shader Textures Handled")
      return {'FINISHED'}

   def process_texture(self, node, source_folder, destination_folder, base_image_name):
      # Assume .png extension for the source, can be expanded to check other formats
      source_texture_path = os.path.join(source_folder, base_image_name + ".png")

      if not os.path.exists(source_texture_path):
         self.report({'ERROR'}, f"Texture not found: {source_texture_path}")
         return None

      # Generate new texture name and path
      generic_name = self.generate_generic_name(destination_folder, base_image_name)
      destination_texture_path = os.path.join(destination_folder, generic_name)

      # Copy and rename the texture if it doesn't exist in the destination
      if not os.path.exists(destination_texture_path):
         shutil.copy(source_texture_path, destination_texture_path)
         print(f"Texture copied and renamed to: {destination_texture_path}")

      return destination_texture_path

   def generate_generic_name(self, destination_folder, base_image_name):
      base_name = os.path.basename(destination_folder)
      suffix = 1
      new_name = f"{base_name}_{suffix}.png"

      while os.path.exists(os.path.join(destination_folder, new_name)):
         suffix += 1
         new_name = f"{base_name}_{suffix}.png"

      return new_name

class ForciYakuzaTexturePanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Yakuza Shader Texture Handler"
   bl_idname = "OBJECT_PT_forci_yakuza_texture"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'

   def draw(self, context):
      layout = self.layout
      scene = context.scene
      layout.prop(scene.forci_yakuza_texture_props, "source_folder")
      layout.prop(scene.forci_yakuza_texture_props, "destination_folder")
      layout.operator(ForciYakuzaTextureHandler.bl_idname)

class ForciYakuzaTextureProps(bpy.types.PropertyGroup):
   source_folder: bpy.props.StringProperty(
      name="Source Folder",
      description="Folder where original textures are located",
      subtype='DIR_PATH'
   )
   destination_folder: bpy.props.StringProperty(
      name="Destination Folder",
      description="Folder where processed textures will be placed",
      subtype='DIR_PATH'
   )

def register():
   bpy.utils.register_class(ForciYakuzaTextureHandler)
   bpy.utils.register_class(ForciYakuzaTexturePanel)
   bpy.utils.register_class(ForciYakuzaTextureProps)
   bpy.types.Scene.forci_yakuza_texture_props = bpy.props.PointerProperty(type=ForciYakuzaTextureProps)

def unregister():
   bpy.utils.unregister_class(ForciYakuzaTextureHandler)
   bpy.utils.unregister_class(ForciYakuzaTexturePanel)
   bpy.utils.unregister_class(ForciYakuzaTextureProps)
   del bpy.types.Scene.forci_yakuza_texture_props

if __name__ == "__main__":
   register()
