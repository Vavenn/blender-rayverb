import bpy #type:ignore

def createreciever(id):
    import bmesh# type:ignore
    sphere_mesh = bpy.data.meshes.new('Rayverb - Receiver')
    temp_sphere_receiver = bpy.data.objects.new("Rayverb - Receiver", sphere_mesh)
    bpy.context.collection.objects.link(temp_sphere_receiver)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=16, radius=1)
    bm.to_mesh(sphere_mesh)
    bm.free() 
    empty_obj = temp_sphere_receiver
    empty_obj.name = "Rayverb - Receiver"
    empty_obj.show_name = True 

    empty_obj["_RNA_UI"] = empty_obj.get("_RNA_UI", {})  
    empty_obj["is_sound_receiver"] = id 

    empty_obj["_RNA_UI"]["is_sound_receiver"] = {
        "description": "Mark this Empty as a sound receiver",
    }
    # sphere_mesh["_RNA_UI"] = empty_obj.get("_RNA_UI", {}) 
    # sphere_mesh["is_sound_receiver"] = id 
    # sphere_mesh["_RNA_UI"]["is_sound_receiver"] = {
    #     "description": "Mark this Empty as a sound receiver",
    # }

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
reciever_count = 1

max_reciever_id = 0
for obj in bpy.context.scene.objects:
    if "is_sound_receiver" in obj.keys():
        receiver_id = obj.get("is_sound_receiver")
        if receiver_id > max_reciever_id:
            max_reciever_id = receiver_id

createreciever(max_reciever_id+1)


