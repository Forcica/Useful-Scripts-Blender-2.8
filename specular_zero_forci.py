bl_info = {
    "name": "Forci Specular Zero",
    "author": "Forcica",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool",
    "description": "Set Specular to Zero for all Principled BSDF Materials",
    "category": "FORCI STUFF",
}

import bpy

class ForciSpecularZeroOperator(bpy.types.Operator):
    """Set Specular to Zero for all Principled BSDF Materials"""
    bl_idname = "forcica.specular_zero"
    bl_label = "Set Specular to Zero"
    
    def execute(self, context):
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        node.inputs['Specular'].default_value = 0.0
        self.report({'INFO'}, "Specular set to zero for all Principled BSDF materials")
        return {'FINISHED'}

class ForciSpecularZeroPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Specular Zero"
    bl_idname = "MATERIAL_PT_forci_specular_zero"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FORCI STUFF'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(ForciSpecularZeroOperator.bl_idname)

def register():
    bpy.utils.register_class(ForciSpecularZeroOperator)
    bpy.utils.register_class(ForciSpecularZeroPanel)

def unregister():
    bpy.utils.unregister_class(ForciSpecularZeroOperator)
    bpy.utils.unregister_class(ForciSpecularZeroPanel)

if __name__ == "__main__":
    register()
