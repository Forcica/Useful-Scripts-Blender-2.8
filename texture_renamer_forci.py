bl_info = {
   "name": "Forci Texture Renamer",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (2, 80, 0),
   "location": "View3D > Tool",
   "description": "Automatically rename textures connected to Principled BSDF Materials",
   "category": "FORCI STUFF",
}

import bpy
import os
import shutil

class ForciTextureRenamerOperator(bpy.types.Operator):
   """Automatically rename textures connected to Principled BSDF Materials"""
   bl_idname = "forcica.texture_renamer"
   bl_label = "Rename Textures"

   def execute(self, context):
      # Vous pouvez appeler ici la fonction de remplacement
      result = self.replace_textures(context)
      if result:
         self.report({'INFO'}, "Textures replaced successfully")
      else:
         self.report({'ERROR'}, "There was an issue replacing textures")
      return {'FINISHED'}

   def replace_textures(self, context):
      scene = context.scene
      props = scene.forcica_texture_renamer_props

      new_source_folder = props.source_folder_replace
      old_prefix = props.old_prefix
      new_prefix = props.new_prefix

      # Vérifiez que le nouveau dossier source est défini
      if not new_source_folder:
         self.report({'ERROR'}, "New source folder is not set")
         return False

      # Parcourez tous les matériaux de la scène
      for mat in bpy.data.materials:
         if not mat.use_nodes:
               continue
         for node in mat.node_tree.nodes:
               if node.type == 'TEX_IMAGE' and node.image:
                  # Remplacez l'ancien préfixe par le nouveau dans le nom de la texture
                  old_name = node.image.name
                  if old_prefix in old_name:
                     new_name = old_name.replace(old_prefix, new_prefix)
                     new_path = os.path.join(new_source_folder, new_name)
                     if os.path.exists(new_path):
                           # Chargez la nouvelle image et mettez à jour le nœud
                           new_image = bpy.data.images.load(new_path)
                           node.image = new_image
                           node.image.name = new_name
                     else:
                           self.report({'WARNING'}, f"Texture not found: {new_path}")
      return True

   def rename_texture(self, material, texture_path, destination_folder):
      # Obtient le nom de base du dossier de destination
      destination_basename = os.path.basename(os.path.normpath(destination_folder))

      # Construit un nouveau nom de fichier basé sur le nom du dossier de destination
      new_texture_base_name = f"{destination_basename}_"
      texture_extension = '.png'  # ou vous pouvez extraire l'extension du fichier original si nécessaire
      new_texture_name = new_texture_base_name + texture_extension

      # Vérifie si le fichier existe déjà avec ce nom de base et ajoute un compteur si nécessaire
      counter = 1
      new_texture_path = os.path.join(destination_folder, new_texture_name)
      while os.path.exists(new_texture_path):
         new_texture_name = f"{new_texture_base_name}{counter}{texture_extension}"
         new_texture_path = os.path.join(destination_folder, new_texture_name)
         counter += 1

      # Copie le fichier dans le dossier de destination avec le nouveau nom
      shutil.copy2(texture_path, new_texture_path)

      return new_texture_path


   def update_texture_node(self, context, material, principled_node, new_texture_path):
      bpy.data.images.load(new_texture_path)
      new_texture = bpy.data.images.get(os.path.basename(new_texture_path))
      texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
      texture_node.image = new_texture
      material.node_tree.links.new(principled_node.inputs['Base Color'], texture_node.outputs['Color'])

class ForciTextureRenamerPanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Texture Replacement (Name & Location)"
   bl_idname = "MATERIAL_PT_forci_texture_renamer"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'
   
   def draw(self, context):
      layout = self.layout
      scene = context.scene
      props = scene.forcica_texture_renamer_props

      layout.prop(props, "source_folder")
      layout.prop(props, "destination_folder")
      layout.prop(props, "source_folder_replace")
      layout.prop(props, "old_prefix")
      layout.prop(props, "new_prefix")
      layout.operator(ForciTextureRenamerOperator.bl_idname)

class ForciTextureRenamerProps(bpy.types.PropertyGroup):
   source_folder: bpy.props.StringProperty(
      name="Source Folder",
      description="Folder where original textures are located",
      subtype='DIR_PATH'
   ) # type: ignore
   destination_folder: bpy.props.StringProperty(
      name="Destination Folder",
      description="Folder where renamed textures will be saved",
      subtype='DIR_PATH'
   )  # type: ignore
   source_folder_replace: bpy.props.StringProperty(
      name="Replacement Source Folder",
      description="Folder where new textures are located after renaming",
      subtype='DIR_PATH'
   ) # type: ignore
   old_prefix: bpy.props.StringProperty(
      name="Old Prefix",
      description="The old prefix to find in the texture names",
      default="oldword_"
   ) # type: ignore
   new_prefix: bpy.props.StringProperty(
      name="New Prefix",
      description="The new prefix to replace the old one in the texture names",
      default="newword_"
   ) # type: ignore

def register():
   bpy.utils.register_class(ForciTextureRenamerOperator)
   bpy.utils.register_class(ForciTextureRenamerPanel)
   bpy.utils.register_class(ForciTextureRenamerProps)
   bpy.types.Scene.forcica_texture_renamer_props = bpy.props.PointerProperty(type=ForciTextureRenamerProps)

def unregister():
   bpy.utils.unregister_class(ForciTextureRenamerOperator)
   bpy.utils.unregister_class(ForciTextureRenamerPanel)
   bpy.utils.unregister_class(ForciTextureRenamerProps)
   del bpy.types.Scene.forcica_texture_renamer_props

if __name__ == "__main__":
   register()
