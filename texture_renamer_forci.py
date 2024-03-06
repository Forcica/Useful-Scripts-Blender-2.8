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
      scene = context.scene
      source_folder = scene.forcica_texture_renamer_props.source_folder
      destination_folder = scene.forcica_texture_renamer_props.destination_folder

      if not os.path.exists(destination_folder):
         os.makedirs(destination_folder)

      processed_textures = {}  # Dictionary to store original and new file paths

      for material in bpy.data.materials:
         if material.use_nodes:
               for node in material.node_tree.nodes:
                  if node.type == 'BSDF_PRINCIPLED' and node.inputs.get('Base Color') and node.inputs['Base Color'].is_linked:
                     texture_node = node.inputs['Base Color'].links[0].from_node
                     if texture_node.type == 'TEX_IMAGE':
                           texture_path = bpy.path.abspath(texture_node.image.filepath)
                           if os.path.isfile(texture_path):
                              # Check if the texture was already processed
                              if texture_path not in processed_textures:
                                 new_texture_path = self.rename_texture(material, texture_path, destination_folder)
                                 processed_textures[texture_path] = new_texture_path
                              else:
                                 # Use the existing texture path if it was already processed
                                 new_texture_path = processed_textures[texture_path]

                              # Update the texture node with the new or existing path
                              self.update_texture_node(context, material, node, new_texture_path)
                           else:
                              self.report({'ERROR'}, f"Texture file not found: {texture_path}")

      self.report({'INFO'}, "Textures renamed successfully")
      return {'FINISHED'}

   def rename_texture(self, material, texture_path, destination_folder):
      base_name = os.path.basename(texture_path)
      texture_extension = os.path.splitext(base_name)[1]
      destination_basename = os.path.basename(os.path.normpath(destination_folder))
      new_texture_base_name = f"{destination_basename}_"
      new_texture_name = f"{new_texture_base_name}{texture_extension}"

      # Vérifiez d'abord si une texture renommée existe déjà dans le dossier de destination
      existing_files = [f for f in os.listdir(destination_folder) if os.path.isfile(os.path.join(destination_folder, f))]
      existing_files_base_names = [os.path.splitext(f)[0] for f in existing_files]

      # Si le fichier existe déjà avec le nom de base, trouve le plus grand index utilisé
      indices = [int(name.split('_')[-1]) for name in existing_files_base_names if name.startswith(new_texture_base_name) and name.split('_')[-1].isdigit()]
      max_index = max(indices) if indices else 0

      new_texture_path = os.path.join(destination_folder, new_texture_name)
      if os.path.exists(new_texture_path):
         # Si une texture avec le nom de base sans indice existe, commencez avec le prochain indice disponible
         new_texture_name = f"{new_texture_base_name}{max_index + 1}{texture_extension}"
         new_texture_path = os.path.join(destination_folder, new_texture_name)

      # Si aucune texture n'existe avec le nom, ou si toutes les textures existantes ont un indice
      # Nous devons alors copier la texture avec le nom de base si max_index est 0, sinon avec le prochain indice disponible
      if not max_index or not os.path.exists(new_texture_path):
         shutil.copy2(texture_path, new_texture_path)

      return new_texture_path

   def update_texture_node(self, context, material, principled_node, new_texture_path):
      new_texture = bpy.data.images.load(new_texture_path, check_existing=True)
      principled_node.inputs['Base Color'].links[0].from_node.image = new_texture

class ForciTextureReplacerOperator(bpy.types.Operator):
   """Automatically replace textures connected to Principled BSDF Materials"""
   bl_idname = "forcica.texture_replacer"
   bl_label = "Replace Duplicate Material Names"

   def execute(self, context):
      scene = context.scene
      replace_source_folder = scene.forcica_texture_renamer_props.replace_source_folder
      old_prefix = scene.forcica_texture_renamer_props.old_prefix
      new_prefix = scene.forcica_texture_renamer_props.new_prefix

      for material in bpy.data.materials:
         if material.use_nodes:
               for node in material.node_tree.nodes:
                  if node.type == 'BSDF_PRINCIPLED' and node.inputs.get('Base Color') and node.inputs['Base Color'].is_linked:
                     texture_node = node.inputs['Base Color'].links[0].from_node
                     if texture_node.type == 'TEX_IMAGE':
                           old_texture_path = bpy.path.abspath(texture_node.image.filepath)
                           if old_prefix in old_texture_path:
                              new_texture_path = old_texture_path.replace(old_prefix, new_prefix)
                              if os.path.isfile(new_texture_path):
                                 self.update_texture_node(context, material, node, new_texture_path)
                              else:
                                 self.report({'ERROR'}, f"New texture file not found: {new_texture_path}")

      self.report({'INFO'}, "Textures replaced successfully")
      return {'FINISHED'}

   def update_texture_node(self, context, material, principled_node, new_texture_path):
      new_texture = bpy.data.images.load(new_texture_path, check_existing=True)
      for node in material.node_tree.nodes:
         if node.type == 'TEX_IMAGE' and node.image and node.image.filepath == principled_node.inputs['Base Color'].links[0].from_node.image.filepath:
               node.image = new_texture

class ForciMaterialMergerOperator(bpy.types.Operator):
   """Merge material duplicates into the original one"""
   bl_idname = "forcica.material_merger"
   bl_label = "Merge Material Duplicates"

   def execute(self, context):
      # Obtenir tous les matériaux qui ne finissent pas par un numéro de type .001, .002, etc.
      original_materials = {m.name: m for m in bpy.data.materials if not m.name.split('.')[-1].isdigit()}

      # Réassigner les utilisateurs de matériaux doublons au matériau d'origine
      for mat in bpy.data.materials:
         # Ignorer les matériaux originaux
         if mat.name in original_materials:
               continue
         
         # Trouver le matériau original correspondant (sans suffixe)
         base_name = mat.name.rsplit('.', 1)[0]
         if base_name in original_materials:
               original_mat = original_materials[base_name]
               # Parcourir tous les objets et remplacer les matériaux doublons
               for obj in bpy.data.objects:
                  for slot in obj.material_slots:
                     if slot.material.name == mat.name:
                           slot.material = original_mat
               # Supprimer le matériau doublon après avoir réassigné tous ses utilisateurs
               bpy.data.materials.remove(mat)

      self.report({'INFO'}, "Materials merged successfully")
      return {'FINISHED'}

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
      layout.prop(scene.forcica_texture_renamer_props, "source_folder")
      layout.prop(scene.forcica_texture_renamer_props, "destination_folder")
      layout.operator(ForciTextureRenamerOperator.bl_idname)
      layout.operator(ForciMaterialMergerOperator.bl_idname)

class ForciTextureReplacerPanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Texture Replacement (Prefix)"
   bl_idname = "MATERIAL_PT_forci_texture_replacer"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'

   def draw(self, context):
      layout = self.layout
      scene = context.scene
      layout.prop(scene.forcica_texture_renamer_props, "replace_source_folder")
      layout.prop(scene.forcica_texture_renamer_props, "old_prefix")
      layout.prop(scene.forcica_texture_renamer_props, "new_prefix")
      layout.operator(ForciTextureReplacerOperator.bl_idname)

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
   ) # type: ignore
   replace_source_folder: bpy.props.StringProperty(
      name="Replacement Source Folder",
      description="Folder where new textures are located",
      subtype='DIR_PATH'
   ) # type: ignore
   old_prefix: bpy.props.StringProperty(
      name="Old Prefix",
      description="Old prefix in texture filenames to be replaced",
   ) # type: ignore
   new_prefix: bpy.props.StringProperty(
      name="New Prefix",
      description="New prefix to replace the old prefix in texture filenames",
   )  # type: ignore

def register():
   bpy.utils.register_class(ForciTextureRenamerOperator)
   bpy.utils.register_class(ForciTextureReplacerOperator)
   bpy.utils.register_class(ForciMaterialMergerOperator)  # Ajout de cette ligne
   bpy.utils.register_class(ForciTextureRenamerPanel)
   bpy.utils.register_class(ForciTextureReplacerPanel)
   bpy.utils.register_class(ForciTextureRenamerProps)
   bpy.types.Scene.forcica_texture_renamer_props = bpy.props.PointerProperty(type=ForciTextureRenamerProps)

def unregister():
   bpy.utils.unregister_class(ForciTextureRenamerOperator)
   bpy.utils.unregister_class(ForciTextureReplacerOperator)
   bpy.utils.unregister_class(ForciMaterialMergerOperator)  # Ajout de cette ligne
   bpy.utils.unregister_class(ForciTextureRenamerPanel)
   bpy.utils.unregister_class(ForciTextureReplacerPanel)
   bpy.utils.unregister_class(ForciTextureRenamerProps)
   del bpy.types.Scene.forcica_texture_renamer_props

if __name__ == "__main__":
   register()