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
    
    # This is the property where the material name is stored
    material_name: bpy.props.StringProperty(name="Material Name", default="")
    
    def execute(self, context):
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Get the material name from the WindowManager
        mat_name = context.window_manager.material_name
        
        # Track if any object has been found and selected
        found = False

        # Iterate through all objects in the scene
        for obj in context.scene.objects:
            # Check if the object has materials and is of type 'MESH'
            if obj.type == 'MESH' and obj.data.materials:
                # Iterate through the materials of the object
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.name == mat_name:
                        # Select the object
                        obj.select_set(True)
                        found = True
                        # Set active object to the last selected
                        context.view_layer.objects.active = obj
                        
        # If no objects were found, report it
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
                
                # Connect Principled BSDF to Material Output
                node_tree.links.new(principled_nodes[0].outputs['BSDF'], output_node.inputs['Surface'])
                
                # Connect Texture to Principled BSDF Base Color
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
        
        # Select by Material Name
        layout.prop(wm, "material_name")
        layout.operator(SelectObjectsByMaterialNameOperator.bl_idname)

        # Select by Texture Name
        layout.prop(wm, "texture_name")
        layout.operator(SelectObjectsByTextureNameOperator.bl_idname)
        
        # Reconnect Principled BSDF
        layout.operator(ReconnectPrincipledBSDFOperator.bl_idname)
        
        # Select Objects Without Materials
        layout.operator(SelectObjectsWithoutMaterialsOperator.bl_idname)

def register():
    bpy.utils.register_class(SelectObjectsByMaterialNameOperator)
    bpy.utils.register_class(SelectObjectsByTextureNameOperator)
    bpy.utils.register_class(ReconnectPrincipledBSDFOperator)
    bpy.utils.register_class(SelectObjectsByMaterialAndTexturePanel)
    bpy.utils.register_class(SelectObjectsWithoutMaterialsOperator)
    bpy.types.WindowManager.material_name = bpy.props.StringProperty(name="Material Name", default="")
    bpy.types.WindowManager.texture_name = bpy.props.StringProperty(name="Texture Name", default="")

def unregister():
    bpy.utils.unregister_class(SelectObjectsByMaterialNameOperator)
    bpy.utils.unregister_class(SelectObjectsByTextureNameOperator)
    bpy.utils.unregister_class(ReconnectPrincipledBSDFOperator)
    bpy.utils.unregister_class(SelectObjectsByMaterialAndTexturePanel)
    bpy.utils.unregister_class(SelectObjectsWithoutMaterialsOperator)
    del bpy.types.WindowManager.material_name
    del bpy.types.WindowManager.texture_name

if __name__ == "__main__":
    register()
