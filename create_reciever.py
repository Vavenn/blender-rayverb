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
    # Get the active object (which should be the newly created Empty)
    empty_obj = temp_sphere_receiver

    # Set the name of the Empty object
    empty_obj.name = "Rayverb - Receiver"

    # Make the name visible in the viewport
    empty_obj.show_name = True  # This ensures the name is always visible

    # Add the "is_sound_receiver" property
    empty_obj["_RNA_UI"] = empty_obj.get("_RNA_UI", {})  # Ensure _RNA_UI exists
    empty_obj["is_sound_receiver"] = id 

    # Define how the property appears in Custom Properties
    empty_obj["_RNA_UI"]["is_sound_receiver"] = {
        "description": "Mark this Empty as a sound receiver",
    }
    sphere_mesh["_RNA_UI"] = empty_obj.get("_RNA_UI", {})  # Ensure _RNA_UI exists
    sphere_mesh["is_sound_receiver"] = id 
    sphere_mesh["_RNA_UI"]["is_sound_receiver"] = {
        "description": "Mark this Empty as a sound receiver",
    }

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
reciever_count = 1

# Iterate through all objects in the current scene
for obj in bpy.context.scene.objects:
    if "is_sound_receiver" in obj.keys():
        reciever_count += 1

createreciever(reciever_count)


