bl_info = {
    "name": "Forci Texture Replacer",
    "author": "Forcica",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool > Forci Stuff",
    "description": "Replace .dds Textures with .png in Principled BSDF for all objects in the scene",
    "category": "FORCI STUFF",
}

import bpy
import os

class ForciTextureReplaceOperator(bpy.types.Operator):
    bl_idname = "forcica.texture_replace_operator"
    bl_label = "Replace Textures"

    def execute(self, context):
        # Get the texture directory from the addon preferences
        texture_directory = context.preferences.addons[__name__].preferences.forcica_texture_directory

        # Iterate through all objects in the scene
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                # Iterate through the materials of the object
                for material_slot in obj.material_slots:
                    material = material_slot.material
                    if material.use_nodes:
                        # Iterate through the nodes of the material
                        for node in material.node_tree.nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                # Check if the Base Color input is linked to an image texture node
                                base_color_input = node.inputs["Base Color"]
                                if base_color_input.is_linked:
                                    linked_node = base_color_input.links[0].from_node
                                    if linked_node.type == 'TEX_IMAGE':
                                        image = linked_node.image
                                        if image:
                                            extensions = ['.dds', '.dds.001', '.dds.002', '.dds.003', '.dds.004', '.dds.005']
                                            if any(image.filepath.lower().endswith(ext) for ext in extensions):
                                                # Remove the .dds extensions from the image name
                                                base_name = os.path.splitext(image.name)[0]
                                                for ext in extensions:
                                                    base_name = base_name.replace(ext, '')
                                                png_filename = base_name + ".png"

                                                # Get the full path to the PNG file using os.path.join
                                                png_filepath = os.path.join(texture_directory, png_filename)

                                                if os.path.isfile(png_filepath):
                                                    new_img = bpy.data.images.load(png_filepath)

                                                    # Create a new Image Texture node and add it to Shading
                                                    new_texture_node = material.node_tree.nodes.new(type="ShaderNodeTexImage")
                                                    new_texture_node.image = new_img

                                                    # Link the new Image Texture node to the Base Color input
                                                    material.node_tree.links.new(new_texture_node.outputs["Color"], node.inputs["Base Color"])
                                                    self.report({'INFO'}, f"Replaced texture {image.name} with {png_filename}")
                                                else:
                                                    self.report({'WARNING'}, f"PNG texture {png_filename} not found in directory")

        return {'FINISHED'}

class ForciTextureReplacePanel(bpy.types.Panel):
    bl_label = "Texture Replacer (DDS to PNG)"
    bl_idname = "OBJECT_PT_forci_texture_replacer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FORCI STUFF'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.preferences.addons[__name__].preferences, "forcica_texture_directory", text="Texture Directory")
        layout.operator(ForciTextureReplaceOperator.bl_idname)

class ForciTexturePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    forcica_texture_directory: bpy.props.StringProperty(
        name="Texture Directory",
        subtype='DIR_PATH'
    )

def register():
    bpy.utils.register_class(ForciTextureReplaceOperator)
    bpy.utils.register_class(ForciTextureReplacePanel)
    bpy.utils.register_class(ForciTexturePreferences)

def unregister():
    bpy.utils.unregister_class(ForciTextureReplaceOperator)
    bpy.utils.unregister_class(ForciTextureReplacePanel)
    bpy.utils.unregister_class(ForciTexturePreferences)

if __name__ == "__main__":
    register()
