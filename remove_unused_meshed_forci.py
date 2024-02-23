bl_info = {
    "name": "Forcica Remove Unused Mesh",
    "author": "Forcica",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool",
    "description": "Remove Meshes with Specific Texture Names",
    "category": "FORCI STUFF",
}

import bpy

class ForcicaRemoveMeshOperator(bpy.types.Operator):
    """Remove Meshes with Specific Texture Names"""
    bl_idname = "forcica.remove_mesh"
    bl_label = "Remove Meshes"
    
    texture_name: bpy.props.StringProperty(
        name="Texture Name to Remove",
        description="Enter the name of the texture to remove",
        default="gfdDefaultMat0"
    )
    
    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and self.texture_name in slot.material.name:
                        bpy.context.collection.objects.unlink(obj)
                        bpy.data.objects.remove(obj)
                        break
        
        bpy.context.view_layer.update()
        self.report({'INFO'}, f"Removed meshes with texture name containing '{self.texture_name}'")
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
        layout.use_property_split = True  # Split properties into separate columns
        layout.use_property_decorate = False  # Do not add decorations like angles
        
        col = layout.column()
        col.prop(context.scene.forcica_remove_mesh_settings, "texture_name")
        col.operator(ForcicaRemoveMeshOperator.bl_idname)

class ForcicaRemoveMeshSettings(bpy.types.PropertyGroup):
    texture_name: bpy.props.StringProperty(
        name="Texture Name to Remove",
        description="Enter the name of the texture to remove",
        default="gfdDefaultMat0"
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
