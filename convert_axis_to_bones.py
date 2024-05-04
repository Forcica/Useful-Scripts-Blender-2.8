bl_info = {
   "name": "ForciPM Rigging Tool",
   "author": "Forcica",
   "version": (1, 0),
   "blender": (4, 1, 0),
   "location": "View3D > Sidebar > ForciPM Tab",
   "description": "Automatically creates a rigged armature from a hierarchy of empties.",
   "warning": "",
   "doc_url": "",
   "category": "Rigging",
}

import bpy
from mathutils import Vector # type: ignore

# Le mappage des noms des objets Empty aux noms des bones
empty_to_bone_mapping = {
   "ball_l": "ValveBiped.Bip01_L_Toe0",
   "ball_r": "ValveBiped.Bip01_R_Toe0",
   "ik_foot_r": "ValveBiped.Bip01_R_Foot",
   "ik_foot_l": "ValveBiped.Bip01_L_Foot",
   "calf_r": "ValveBiped.Bip01_R_Calf",
   "calf_l": "ValveBiped.Bip01_L_Calf",
   "thigh_l": "ValveBiped.Bip01_L_Thigh",
   "thigh_r": "ValveBiped.Bip01_R_Thigh",
   "pelvis": "ValveBiped.Bip01_Pelvis",
   "spine_01": "ValveBiped.Bip01_Spine",
   "spine_02": "ValveBiped.Bip01_Spine1",
   "spine_03": "ValveBiped.Bip01_Spine2",
   "neck_01": "ValveBiped.Bip01_Neck1",
   "head": "ValveBiped.Bip01_Head1",
   "clavicle_r": "ValveBiped.Bip01_R_Clavicle",
   "upperarm_r": "ValveBiped.Bip01_R_UpperArm",
   "lowerarm_r": "ValveBiped.Bip01_R_Forearm",
   "ik_hand_r": "ValveBiped.Bip01_R_Hand",
   "thumb_01_r": "ValveBiped.Bip01_R_Finger0",
   "thumb_02_r": "ValveBiped.Bip01_R_Finger01",
   "thumb_03_r": "ValveBiped.Bip01_R_Finger02",
   "index_01_r": "ValveBiped.Bip01_R_Finger1",
   "index_02_r": "ValveBiped.Bip01_R_Finger11",
   "index_03_r": "ValveBiped.Bip01_R_Finger12",
   "middle_01_r": "ValveBiped.Bip01_R_Finger2",
   "middle_02_r": "ValveBiped.Bip01_R_Finger21",
   "middle_03_r": "ValveBiped.Bip01_R_Finger22",
   "ring_01_r": "ValveBiped.Bip01_R_Finger3",
   "ring_02_r": "ValveBiped.Bip01_R_Finger31",
   "ring_03_r": "ValveBiped.Bip01_R_Finger32",
   "pinky_01_r": "ValveBiped.Bip01_R_Finger4",
   "pinky_02_r": "ValveBiped.Bip01_R_Finger41",
   "pinky_03_r": "ValveBiped.Bip01_R_Finger42",
   "clavicle_l": "ValveBiped.Bip01_L_Clavicle",
   "upperarm_l": "ValveBiped.Bip01_L_UpperArm",
   "lowerarm_l": "ValveBiped.Bip01_L_Forearm",
   "ik_hand_l": "ValveBiped.Bip01_L_Hand",
   "thumb_01_l": "ValveBiped.Bip01_L_Finger0",
   "thumb_02_l": "ValveBiped.Bip01_L_Finger01",
   "thumb_03_l": "ValveBiped.Bip01_L_Finger02",
   "index_01_l": "ValveBiped.Bip01_L_Finger1",
   "index_02_l": "ValveBiped.Bip01_L_Finger11",
   "index_03_l": "ValveBiped.Bip01_L_Finger12",
   "middle_01_l": "ValveBiped.Bip01_L_Finger2",
   "middle_02_l": "ValveBiped.Bip01_L_Finger21",
   "middle_03_l": "ValveBiped.Bip01_L_Finger22",
   "ring_01_l": "ValveBiped.Bip01_L_Finger3",
   "ring_02_l": "ValveBiped.Bip01_L_Finger31",
   "ring_03_l": "ValveBiped.Bip01_L_Finger32",
   "pinky_01_l": "ValveBiped.Bip01_L_Finger4",
   "pinky_02_l": "ValveBiped.Bip01_L_Finger41",
   "pinky_03_l": "ValveBiped.Bip01_L_Finger42",
}


def copy_animation_to_bones(armature_obj, bone_name, action):
   pose_bone = armature_obj.pose.bones.get(bone_name)
   if pose_bone is None:
      print(f"Warning: Bone {bone_name} not found in the armature. Skipping animation.")
      return

   # Ensure the armature has an action to store the keyframes
   if not armature_obj.animation_data:
      armature_obj.animation_data_create()
   if not armature_obj.animation_data.action:
      armature_obj.animation_data.action = bpy.data.actions.new(name=f"{armature_obj.name}_Action")

   for fcurve in action.fcurves:
      path_split = fcurve.data_path.rsplit('.', 1)
      if len(path_split) != 2:
         # If the fcurve data path does not split into two parts, it's not valid for bone animation
         continue

      property = path_split[1]
      bone_data_path = f'pose.bones["{bone_name}"].{property}'
      bone_fcurve = armature_obj.animation_data.action.fcurves.find(bone_data_path, index=fcurve.array_index)

      if bone_fcurve is None:
         bone_fcurve = armature_obj.animation_data.action.fcurves.new(bone_data_path, index=fcurve.array_index)

      # Copy keyframe points
      bone_fcurve.keyframe_points.clear()
      for keyframe in fcurve.keyframe_points:
         bone_fcurve.keyframe_points.insert(frame=keyframe.co.x, value=keyframe.co.y, options={'FAST'})

      bone_fcurve.update()

def create_rigged_armature(context):
   root_empty = context.active_object

   if not root_empty or root_empty.type != 'EMPTY':
      print("Please select the root empty object.")
      return

   # Create an armature and enter edit mode
   bpy.ops.object.armature_add()
   armature_obj = context.object
   armature_obj.show_in_front = True
   bpy.context.view_layer.objects.active = armature_obj
   bpy.ops.object.mode_set(mode='EDIT')

   edit_bones = armature_obj.data.edit_bones

   # Create bones from empties listed in the mapping
   bone_mapping = {}
   for empty_obj in context.scene.objects:
      if empty_obj.type == 'EMPTY':
            bone_name = empty_to_bone_mapping.get(empty_obj.name, empty_obj.name)
            bone = edit_bones.new(bone_name)
            bone.head = empty_obj.matrix_world.translation
            bone.tail = bone.head + Vector((0, 0, 0.1)) # Small offset to create the bone tail
            bone_mapping[empty_obj] = bone

   # Parent bones based on the empties' hierarchy
   for empty_obj, bone in bone_mapping.items():
      parent_empty = empty_obj.parent
      if parent_empty and parent_empty in bone_mapping:
            bone.parent = bone_mapping[parent_empty]
            bone.use_connect = False  # You can set True if you want connected bones

   # Leave edit mode to save the bones
   bpy.ops.object.mode_set(mode='OBJECT')
   if not armature_obj.animation_data:
      armature_obj.animation_data_create()
   armature_action = bpy.data.actions.new(name="ArmatureAction")
   armature_obj.animation_data.action = armature_action

   # Switch to pose mode to apply pose bone transformations
   bpy.ops.object.mode_set(mode='POSE')

   # Copy animations from empties to the corresponding bones in the armature
   for empty_name, bone_name in empty_to_bone_mapping.items():
      if empty_name in context.scene.objects:
         empty_obj = context.scene.objects[empty_name]
         if empty_obj.animation_data and empty_obj.animation_data.action:
               copy_animation_to_bones(armature_obj, bone_name, empty_obj.animation_data.action)

   # Switch back to object mode
   bpy.ops.object.mode_set(mode='OBJECT')

class OBJECT_OT_CreateRiggedArmature(bpy.types.Operator):
   bl_idname = "object.create_rigged_armature_operator"
   bl_label = "Create Rigged Armature"
   bl_options = {'REGISTER', 'UNDO'}

   def execute(self, context):
      create_rigged_armature(context)
      return {'FINISHED'}

class ForciPM_PT_Panel(bpy.types.Panel):
   bl_label = "ForciPM Rigging Tool"
   bl_idname = "FORCIPM_PT_panel"
   bl_space_type = 'VIEW_3D'
   bl_region_type = 'UI'
   bl_category = 'ForciPM'

   def draw(self, context):
      layout = self.layout
      layout.operator(OBJECT_OT_CreateRiggedArmature.bl_idname, text="Create Rigged Armature")

def register():
   bpy.utils.register_class(OBJECT_OT_CreateRiggedArmature)
   bpy.utils.register_class(ForciPM_PT_Panel)

def unregister():
   bpy.utils.unregister_class(OBJECT_OT_CreateRiggedArmature)
   bpy.utils.unregister_class(ForciPM_PT_Panel)

if __name__ == "__main__":
   register()