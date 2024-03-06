bl_info = {
   "name": "Replace and Create Collection Name",
   "author": "Forcica",
   "version": (1, 1),
   "blender": (2, 80, 0),
   "location": "View3D > N Panel > FORCI STUFF",
   "description": "Replace words in collection names and create new collections",
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
   base_word: bpy.props.StringProperty(
      name="Base Word",
      description="Base word for new collection names",
      default=""
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

class ForciCreateCollectionsFromSelectionOperator(bpy.types.Operator):
    """Create collections from selected objects"""
    bl_idname = "forcica.create_collections_from_selection"
    bl_label = "Create Collections From Selection"
    
    collection_name: bpy.props.StringProperty(name="Collection Name", default="")

    def execute(self, context):
        # Récupérer les maillages sélectionnés
        selected_objects = bpy.context.selected_objects
        
        # Récupérer le nom de la collection parente
        parent_collection_name = bpy.context.scene.collection.name
        
        # Récupérer le nom de la collection à créer
        collection_name = self.collection_name
        
        # Créer la collection parente si elle n'existe pas
        if collection_name not in bpy.data.collections:
            parent_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(parent_collection)
        else:
            parent_collection = bpy.data.collections[collection_name]
        
        # Parcourir les maillages sélectionnés
        for index, obj in enumerate(selected_objects):
            # Créer la collection _reference
            reference_collection = bpy.data.collections.new(f"{context.scene.collection_renamer_props.base_word}_{index+1}_reference")
            parent_collection.children.link(reference_collection)
            
            # Créer la collection _phys
            phys_collection = bpy.data.collections.new(f"{context.scene.collection_renamer_props.base_word}_{index+1}_phys")
            parent_collection.children.link(phys_collection)
            
            # Ajouter le maillage à la collection _reference
            reference_collection.objects.link(obj)
            
        return {'FINISHED'}

class ForciCollectionNamePanel(bpy.types.Panel):
   """Creates a Panel in the Object properties window"""
   bl_label = "Replace and Create Collection Name"
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

      layout.separator()
      
      layout.prop(props, "base_word", text="Collection Name")  
      layout.operator(ForciCreateCollectionsFromSelectionOperator.bl_idname)

def register():
   bpy.utils.register_class(ForciCollectionRenamerProps)
   bpy.types.Scene.collection_renamer_props = bpy.props.PointerProperty(type=ForciCollectionRenamerProps)
   bpy.utils.register_class(ForciCollectionRenamerOperator)
   bpy.utils.register_class(ForciCreateCollectionsFromSelectionOperator)
   bpy.utils.register_class(ForciCollectionNamePanel)

def unregister():
   bpy.utils.unregister_class(ForciCollectionRenamerProps)
   del bpy.types.Scene.collection_renamer_props
   bpy.utils.unregister_class(ForciCollectionRenamerOperator)
   bpy.utils.unregister_class(ForciCreateCollectionsFromSelectionOperator)
   bpy.utils.unregister_class(ForciCollectionNamePanel)

if __name__ == "__main__":
   register()
