bl_info = {
    "name": "Forci Alpha Changing",
    "author": "Votre nom",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool",
    "description": "Change alpha settings for Principled BSDF Materials",
    "category": "FORCI STUFF",
}

import bpy

class ForciAlphaApplyingOperator(bpy.types.Operator):
    """Apply Alpha Texture to Principled BSDF Material"""
    bl_idname = "forcica.alpha_applying"
    bl_label = "Apply Alpha Texture"
    
    def execute(self, context):
        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            for material in obj.data.materials:
                if material.use_nodes:
                    bsdf_node = None
                    image_node = None
                    # Trouver le nœud BSDF Principled et le nœud d'image connecté
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            bsdf_node = node
                        elif node.type == 'TEX_IMAGE':
                            # Vérifier si ce nœud d'image est connecté au Base Color de BSDF Principled
                            for link in material.node_tree.links:
                                if link.from_node == node and link.to_node.type == 'BSDF_PRINCIPLED' and link.to_socket.name == 'Base Color':
                                    image_node = node
                                    break
                    if bsdf_node and image_node:
                        # Connecter le canal Alpha de la texture image au canal Alpha de Principled BSDF
                        alpha_output = image_node.outputs.get('Alpha')
                        alpha_input = bsdf_node.inputs.get('Alpha')
                        if alpha_output and alpha_input:
                            material.node_tree.links.new(alpha_output, alpha_input)
        self.report({'INFO'}, "Alpha texture applied to Principled BSDF materials")
        return {'FINISHED'}

class ForciAlphaBlendOperator(bpy.types.Operator):
    """Toggle Alpha Blend Mode for Material"""
    bl_idname = "forcica.alpha_blend"
    bl_label = "Toggle Alpha Blend Mode"
    
    def execute(self, context):
        # Récupérer l'objet sélectionné
        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            # Parcourir les matériaux de l'objet
            for material in obj.data.materials:
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            # Changer le mode de fusion en Alpha Blend
                            material.blend_method = 'BLEND'
        self.report({'INFO'}, "Alpha Blend mode set for selected materials")
        return {'FINISHED'}

class ForciAlphaChangingPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Alpha ON"
    bl_idname = "MATERIAL_PT_forci_alpha_changing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FORCI STUFF'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(ForciAlphaApplyingOperator.bl_idname)
        layout.operator(ForciAlphaBlendOperator.bl_idname)

def register():
    bpy.utils.register_class(ForciAlphaApplyingOperator)
    bpy.utils.register_class(ForciAlphaBlendOperator)
    bpy.utils.register_class(ForciAlphaChangingPanel)

def unregister():
    bpy.utils.unregister_class(ForciAlphaApplyingOperator)
    bpy.utils.unregister_class(ForciAlphaBlendOperator)
    bpy.utils.unregister_class(ForciAlphaChangingPanel)

if __name__ == "__main__":
    register()
