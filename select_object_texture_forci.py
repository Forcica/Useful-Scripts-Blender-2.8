bl_info = {
   "name": "Select Objects by Material and Texture",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (2, 80, 0),
   "location": "View3D > Tool",
   "description": "Select objects by material name or by texture name and reconnect nodes",
   "category": "FORCI STUFF",
}

import bpy

class SelectObjectsByMaterialNameOperator(bpy.types.Operator):
   """Select objects with the same material name"""
   bl_idname = "object.select_by_material_name"
   bl_label = "Select by Material Name"
   
   material_name: bpy.props.StringProperty(name="Material Name", default="")
   
   def execute(self, context):
      bpy.ops.object.select_all(action='DESELECT')
      
      mat_name = context.window_manager.material_name
      
      found = False

      for obj in context.scene.objects:
         if obj.type == 'MESH' and obj.data.materials:
               for mat_slot in obj.material_slots:
                  if mat_slot.material and mat_slot.material.name == mat_name:
                     obj.select_set(True)
                     found = True
                     context.view_layer.objects.active = obj
                     
      if not found:
         self.report({'WARNING'}, f"No objects found with the material name: {mat_name}")
         return {'CANCELLED'}
      
      return {'FINISHED'}

class SelectObjectsByTextureNameOperator(bpy.types.Operator):
   """Select objects with the specified texture name"""
   bl_idname = "object.select_by_texture_name"
   bl_label = "Select by Texture Name"
   
   texture_name: bpy.props.StringProperty(name="Texture Name", default="")
   
   def execute(self, context):
      bpy.ops.object.select_all(action='DESELECT')
      texture_name = context.window_manager.texture_name
      found = False
      
      for obj in context.scene.objects:
         if obj.type == 'MESH' and obj.data.materials:
               for mat_slot in obj.material_slots:
                  if not mat_slot.material or not mat_slot.material.use_nodes:
                     continue
                  for node in mat_slot.material.node_tree.nodes:
                     if node.type == 'TEX_IMAGE' and node.image and node.image.name == texture_name:
                           obj.select_set(True)
                           context.view_layer.objects.active = obj
                           found = True
                           break
      
      if not found:
         self.report({'WARNING'}, f"No objects found with the texture name: {texture_name}")
         return {'CANCELLED'}
      
      return {'FINISHED'}

class ReconnectPrincipledBSDFOperator(bpy.types.Operator):
   """Reconnect Principled BSDF to Material Output and Texture to Base Color"""
   bl_idname = "object.reconnect_principled_bsdf"
   bl_label = "Reconnect Principled BSDF"
   
   def execute(self, context):
      selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
      
      for obj in selected_objects:
         for mat_slot in obj.material_slots:
               if not mat_slot.material or not mat_slot.material.use_nodes:
                  continue
               node_tree = mat_slot.material.node_tree
               principled_nodes = [node for node in node_tree.nodes if node.type == 'BSDF_PRINCIPLED']
               texture_nodes = [node for node in node_tree.nodes if node.type == 'TEX_IMAGE']
               output_node = node_tree.nodes.get('Material Output')
               
               if not principled_nodes or not output_node:
                  continue
               
               node_tree.links.new(principled_nodes[0].outputs['BSDF'], output_node.inputs['Surface'])
               
               if texture_nodes:
                  node_tree.links.new(texture_nodes[0].outputs['Color'], principled_nodes[0].inputs['Base Color'])
      
      return {'FINISHED'}

class SelectObjectsWithoutMaterialsOperator(bpy.types.Operator):
   """Select objects without materials"""
   bl_idname = "object.select_without_materials"
   bl_label = "Select Objects Without Materials"
   
   def execute(self, context):
      bpy.ops.object.select_all(action='DESELECT')
      found = False
      
      for obj in context.scene.objects:
         if obj.type == 'MESH' and not obj.data.materials:
               obj.select_set(True)
               context.view_layer.objects.active = obj
               found = True
      
      if not found:
         self.report({'WARNING'}, "No objects found without materials")
         return {'CANCELLED'}
      
      return {'FINISHED'}

class ConnectClosestLeftNodeOperator(bpy.types.Operator):
   """Connect the closest left node to the Principled BSDF node for all selected meshes, 
   ensuring shared textures are only connected once."""
   bl_idname = "material.connect_closest_left_node"
   bl_label = "Connect Closest Left Node Once per Shared Texture Node"

   def execute(self, context):
      # Set to keep track of textures that have already been processed
      processed_textures = set()

      # Iterate over all selected objects in the scene
      selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
      for obj in selected_objects:
         # Iterate over all materials in the object
         for mat_slot in obj.material_slots:
            mat = mat_slot.material
            if not mat or not mat.use_nodes:
               continue

            # Get the nodes and links of the material
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Get the Principled BSDF node
            principled_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
            if not principled_node:
               self.report({'WARNING'}, f"Material '{mat.name}' has no Principled BSDF node.")
               continue

            # Check if the Principled BSDF node's 'Base Color' input is linked
            if principled_node.inputs['Base Color'].is_linked:
               base_color_link = principled_node.inputs['Base Color'].links[0]
               texture_node = base_color_link.from_node

               # Check if this texture node's image is already processed
               if texture_node.image and texture_node.image.name in processed_textures:
                  continue

               # If the node has multiple users, we only want to process it once
               if texture_node.image and texture_node.image.users > 1:
                  processed_textures.add(texture_node.image.name)

               # Find the closest left node to the Image Texture node
               left_nodes = [node for node in nodes if node.location.x < texture_node.location.x and node.type != 'OUTPUT_MATERIAL']
               if not left_nodes:
                  self.report({'INFO'}, f"No nodes to the left of the texture node in material '{mat.name}'.")
                  continue

               # Find the closest left node
               closest_left_node = min(left_nodes, key=lambda node: texture_node.location.x - node.location.x)

               # Perform the connection
               for output_socket in closest_left_node.outputs:
                  if output_socket.type == 'RGBA':
                     new_link = links.new(output_socket, principled_node.inputs['Base Color'])
                     if new_link:
                        self.report({'INFO'}, f"Connected '{closest_left_node.name}' to 'Base Color' of '{principled_node.name}' in material '{mat.name}'.")
                     break

      return {'FINISHED'}

class SelectObjectsByMaterialAndTexturePanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Select Objects by Material and Texture"
   bl_idname = "OBJECT_PT_select_by_material_and_texture"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'
   
   def draw(self, context):
      layout = self.layout
      wm = context.window_manager
      
      layout.prop(wm, "material_name")
      layout.operator(SelectObjectsByMaterialNameOperator.bl_idname)

      layout.prop(wm, "texture_name")
      layout.operator(SelectObjectsByTextureNameOperator.bl_idname)
      
      layout.operator(ReconnectPrincipledBSDFOperator.bl_idname)
      
      layout.operator(SelectObjectsWithoutMaterialsOperator.bl_idname)

      layout.operator(ConnectClosestLeftNodeOperator.bl_idname)

def register():
   bpy.utils.register_class(SelectObjectsByMaterialNameOperator)
   bpy.utils.register_class(SelectObjectsByTextureNameOperator)
   bpy.utils.register_class(ReconnectPrincipledBSDFOperator)
   bpy.utils.register_class(SelectObjectsByMaterialAndTexturePanel)
   bpy.utils.register_class(SelectObjectsWithoutMaterialsOperator)
   bpy.utils.register_class(ConnectClosestLeftNodeOperator)  # Assurez-vous que cette ligne est ajoutée
   bpy.types.WindowManager.material_name = bpy.props.StringProperty(name="Material Name", default="")
   bpy.types.WindowManager.texture_name = bpy.props.StringProperty(name="Texture Name", default="")

def unregister():
   bpy.utils.unregister_class(SelectObjectsByMaterialNameOperator)
   bpy.utils.unregister_class(SelectObjectsByTextureNameOperator)
   bpy.utils.unregister_class(ReconnectPrincipledBSDFOperator)
   bpy.utils.unregister_class(SelectObjectsByMaterialAndTexturePanel)
   bpy.utils.unregister_class(SelectObjectsWithoutMaterialsOperator)
   bpy.utils.unregister_class(ConnectClosestLeftNodeOperator)  # Assurez-vous que cette ligne est ajoutée
   del bpy.types.WindowManager.material_name
   del bpy.types.WindowManager.texture_name

if __name__ == "__main__":
   register()
