bl_info = {
   "name": "Forci Yakuza Shader Texture Handler",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (4, 0, 0),
   "location": "View3D > Tool",
   "description": "Handle Yakuza Shader Textures and clean unused textures",
   "category": "FORCI STUFF",
}

import bpy
import os
import shutil
import bmesh  # Import the bmesh module

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
      used_textures_folder = bpy.context.scene.forci_yakuza_texture_props.used_textures_folder

      if not os.path.exists(destination_folder):
         os.makedirs(destination_folder)
      # Cette vérification permet de créer le dossier seulement si le chemin est spécifié
      if used_textures_folder and not os.path.exists(used_textures_folder):
         os.makedirs(used_textures_folder)

      # Existing functionality: process and copy textures
      processed_textures = self.process_textures(source_folder, destination_folder)

      # Use either the selected objects or all objects if none are selected
      objects_to_check = context.selected_objects if context.selected_objects else bpy.data.objects

      # Collect used textures from the objects to check
      used_textures = self.collect_used_textures(objects_to_check)

      # Copy used textures to the used textures folder only if the folder is specified
      if used_textures_folder:  # Condition pour vérifier si le chemin est défini
         for texture_name in used_textures:
            source_texture_path = os.path.join(destination_folder, texture_name + ".png")
            destination_texture_path = os.path.join(used_textures_folder, texture_name + ".png")
            if os.path.exists(source_texture_path) and not os.path.exists(destination_texture_path):
                  shutil.copy(source_texture_path, destination_texture_path)

      # Clean unused materials from the scene
      self.clean_unused_materials()

      self.report({'INFO'}, "Textures processed. Used textures copied and unused materials cleaned as necessary.")
      return {'FINISHED'}

   def process_textures(self, source_folder, destination_folder):
      """
      Process all relevant textures found in the source folder, copy them to the destination folder,
      and update the materials to use the new textures.
      """
      processed_textures = {}
      for material in bpy.data.materials:
         if material.use_nodes:
            for node in material.node_tree.nodes:
                  if node.type == 'TEX_IMAGE' and node.image:
                     base_image_name = os.path.splitext(node.image.name)[0]
                     if base_image_name not in processed_textures:
                        # Pass the material to the process_texture function as well
                        processed_texture_path = self.process_texture(material, node, source_folder, destination_folder, base_image_name)
                        if processed_texture_path:
                              processed_textures[base_image_name] = processed_texture_path
      return processed_textures

   def process_texture(self, material, node, source_folder, destination_folder, base_image_name):
      # Le chemin source de l'image.
      source_texture_path = os.path.join(source_folder, base_image_name + ".png")
      if not os.path.exists(source_texture_path):
         self.report({'ERROR'}, f"Texture not found: {source_texture_path}")
         return None

      # Générer un nom générique pour la nouvelle image et la copier dans le dossier de destination.
      generic_name = self.generate_generic_name(destination_folder, base_image_name)
      destination_texture_path = os.path.join(destination_folder, generic_name)
      if not os.path.exists(destination_texture_path):
         shutil.copy(source_texture_path, destination_texture_path)

      # Charger la nouvelle image dans Blender et créer un node d'image texture.
      new_img = bpy.data.images.load(destination_texture_path)
      new_texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
      new_texture_node.image = new_img
      new_texture_node.location = node.location  # Placer au même endroit que l'ancien node.

      # Trouver le node 'Neo Yakuza Shader' dans le node tree du matériau.
      shader_node = next((n for n in material.node_tree.nodes if "Neo Yakuza Shader" in n.name), None)
      
      if shader_node:
         # L'entrée 'texture_diffuse' du node shader.
         texture_diffuse_input = shader_node.inputs.get("texture_diffuse")
         
         # Supprimer les anciens liens vers 'texture_diffuse'.
         links = material.node_tree.links
         for link in list(links):
            if link.to_node == shader_node and link.to_socket == texture_diffuse_input:
                  links.remove(link)

         # Créer le nouveau lien entre la sortie 'Color' du node d'image texture et l'entrée 'texture_diffuse'.
         links.new(new_texture_node.outputs['Color'], texture_diffuse_input)

      # Supprimer l'ancien node texture s'il s'agit de celui qui est remplacé.
      if node.name in material.node_tree.nodes:
         node.remove(material.node_tree.nodes[node.name])

      # Retourner le chemin d'accès de l'image pour une utilisation ultérieure.
      return destination_texture_path

   def generate_generic_name(self, destination_folder, base_image_name):
      base_name = os.path.basename(destination_folder)
      suffix = 1
      new_name = f"{base_name}_{suffix}.png"
      while os.path.exists(os.path.join(destination_folder, new_name)):
         suffix += 1
         new_name = f"{base_name}_{suffix}.png"
      return new_name

   def collect_used_textures(self, objects):
      bpy.ops.object.mode_set(mode='OBJECT')  # Make sure you're in object mode
      used_textures = set()
      
      for obj in objects:
         if obj.type == 'MESH':
            # Store the material names used for later reference
            used_material_names = set()
            
            # Ensure we're working with the right object
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')  # Go into edit mode
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.faces.ensure_lookup_table()

            for mat_slot in obj.material_slots:
                  mat = mat_slot.material
                  if mat and mat.use_nodes:
                     for node in mat.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                              # Add the texture name to the set if the material is used
                              texture_path = bpy.path.abspath(node.image.filepath)
                              texture_name = os.path.basename(texture_path)
                              used_material_names.add(mat.name)
                              used_textures.add(os.path.splitext(texture_name)[0])

            # Select faces based on materials and check usage
            for mat_index, mat_name in enumerate(used_material_names):
                  bpy.ops.object.mode_set(mode='OBJECT')  # Back to object mode to flush selection
                  for poly in obj.data.polygons:  # Deselect all polys first
                     poly.select = False

                  bpy.ops.object.mode_set(mode='EDIT')  # Back into edit mode to select by material
                  # Select faces with the material
                  for poly in obj.data.polygons:
                     if obj.material_slots[poly.material_index].material.name == mat_name:
                        poly.select = True
                  
                  bmesh.update_edit_mesh(obj.data)

                  # Check if the selected material is actually used by checking if any faces are selected
                  bpy.ops.object.mode_set(mode='OBJECT')  # Back to object mode to get selection state
                  if not any(poly.select for poly in obj.data.polygons):
                     # If no faces use this material, remove associated texture
                     for node in mat.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                              texture_path = bpy.path.abspath(node.image.filepath)
                              texture_name = os.path.basename(texture_path)
                              used_textures.discard(os.path.splitext(texture_name)[0])

            bpy.ops.object.mode_set(mode='OBJECT')  # Make sure to end in object mode

      return used_textures

   def clean_unused_materials(self):
      for material in bpy.data.materials:
         if material.users == 0:
               bpy.data.materials.remove(material)

   def copy_texture(self, texture_name, source_folder, destination_folder):
      source_path = os.path.join(source_folder, texture_name)
      destination_path = os.path.join(destination_folder, texture_name)
      if os.path.isfile(source_path) and not os.path.isfile(destination_path):
         shutil.copy2(source_path, destination_path)

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
      layout.prop(scene.forci_yakuza_texture_props, "used_textures_folder")
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
   used_textures_folder: bpy.props.StringProperty(
      name="Used Textures Folder",
      description="Folder where used textures will be copied",
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

