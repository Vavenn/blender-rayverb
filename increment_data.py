import bpy#type:ignore

max_receiver_id = 0
for obj in bpy.context.scene.objects:
    if "is_sound_receiver" in obj.keys():
        receiver_id = obj.get("is_sound_receiver")
        if receiver_id > max_receiver_id:
            max_receiver_id = receiver_id

min_selected_id = max_receiver_id
for obj in bpy.context.selected_objects:
    if "is_sound_receiver" in obj.keys():
        receiver_id = obj.get("is_sound_receiver")
        if receiver_id < min_selected_id:
            min_selected_id = receiver_id

for obj in bpy.context.selected_objects:
    if "is_sound_receiver" in obj.keys():
        receiver_id = obj.get("is_sound_receiver")
        # print(receiver_id)
        # print(min_selected_id)
        # print(max_receiver_id)
        obj["is_sound_receiver"] = (receiver_id-min_selected_id)+max_receiver_id+1
            
