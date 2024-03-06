bl_info = {
   "name": "Forcica Remove Unused Mesh",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (2, 80, 0),
   "location": "View3D > Tool",
   "description": "Remove Meshes based on material name or lack thereof",
   "category": "FORCI STUFF",
}

import bpy

class ForcicaRemoveMeshOperator(bpy.types.Operator):
   """Remove Meshes based on material name or lack thereof"""
   bl_idname = "forcica.remove_mesh"
   bl_label = "Conditionally Remove Meshes"
   
   texture_name: bpy.props.StringProperty(
      name="Material Name to Check",
      description="Enter the name of the material to remove meshes, leave blank to remove meshes without any materials",
      default=""
   )
   
   def execute(self, context):
      removed_count = 0 
      
      for obj in bpy.context.scene.objects:
         if obj.type == 'MESH':
               if self.texture_name:
                  for slot in obj.material_slots:
                     if slot.material and self.texture_name in slot.material.name:
                           bpy.data.objects.remove(obj, do_unlink=True)
                           removed_count += 1
                           break 
               else: 
                  if all(slot.material is None for slot in obj.material_slots):
                     bpy.data.objects.remove(obj, do_unlink=True)
                     removed_count += 1
      
      self.report({'INFO'}, f"Removed {removed_count} meshes based on criteria")
      return {'FINISHED'}

class ForcicaRemoveMeshPanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Remove Unused Mesh"
   bl_idname = "MATERIAL_PT_forcica_remove_mesh"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'
   
   def draw(self, context):
      layout = self.layout
      layout.use_property_split = True
      layout.use_property_decorate = False
      
      col = layout.column()
      col.prop(context.scene.forcica_remove_mesh_settings, "texture_name")
      col.operator(ForcicaRemoveMeshOperator.bl_idname)

class ForcicaRemoveMeshSettings(bpy.types.PropertyGroup):
   texture_name: bpy.props.StringProperty(
      name="Material Name to Check",
      description="Enter the name of the material to check, leave blank to target meshes without materials",
      default=""
   )

def register():
   bpy.utils.register_class(ForcicaRemoveMeshOperator)
   bpy.utils.register_class(ForcicaRemoveMeshPanel)
   bpy.utils.register_class(ForcicaRemoveMeshSettings)
   bpy.types.Scene.forcica_remove_mesh_settings = bpy.props.PointerProperty(type=ForcicaRemoveMeshSettings)

def unregister():
   bpy.utils.unregister_class(ForcicaRemoveMeshOperator)
   bpy.utils.unregister_class(ForcicaRemoveMeshPanel)
   bpy.utils.unregister_class(ForcicaRemoveMeshSettings)
   del bpy.types.Scene.forcica_remove_mesh_settings

if __name__ == "__main__":
   register()
