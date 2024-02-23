bl_info = {
   "name": "Replace Collection Name",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (2, 80, 0),
   "location": "View3D > N Panel > FORCI STUFF",
   "description": "Replace words in collection names",
   "category": "FORCI STUFF",
}

import bpy

class ForciCollectionRenamerProps(bpy.types.PropertyGroup):
   old_word: bpy.props.StringProperty(
      name="Old Word",
      description="Word to be replaced in the collection names",
      default="AncienMot"
   )
   new_word: bpy.props.StringProperty(
      name="New Word",
      description="New word to use in the collection names",
      default="NouveauMot"
   )

class ForciCollectionRenamerOperator(bpy.types.Operator):
   """Rename collections by replacing words"""
   bl_idname = "forcica.collection_renamer"
   bl_label = "Replace Collection Names"
   
   def execute(self, context):
      props = context.scene.collection_renamer_props
      old_word = props.old_word
      new_word = props.new_word

      for collection in bpy.data.collections:
         if old_word in collection.name:
               collection.name = collection.name.replace(old_word, new_word)

      # Actualiser l'interface utilisateur
      bpy.context.view_layer.update()

      self.report({'INFO'}, "Collections renamed successfully")
      return {'FINISHED'}

class ForciCollectionNamePanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Replace Collection Name"
   bl_idname = "VIEW3D_PT_forci_collection_name"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'FORCI STUFF'
   
   def draw(self, context):
      layout = self.layout
      props = context.scene.collection_renamer_props

      layout.prop(props, "old_word")
      layout.prop(props, "new_word")
      layout.operator(ForciCollectionRenamerOperator.bl_idname)

def register():
   bpy.utils.register_class(ForciCollectionRenamerProps)
   bpy.types.Scene.collection_renamer_props = bpy.props.PointerProperty(type=ForciCollectionRenamerProps)
   bpy.utils.register_class(ForciCollectionRenamerOperator)
   bpy.utils.register_class(ForciCollectionNamePanel)

def unregister():
   bpy.utils.unregister_class(ForciCollectionRenamerProps)
   del bpy.types.Scene.collection_renamer_props
   bpy.utils.unregister_class(ForciCollectionRenamerOperator)
   bpy.utils.unregister_class(ForciCollectionNamePanel)

if __name__ == "__main__":
   register()
