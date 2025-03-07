import bpy #type:ignore

def create_emit():
    # Create a new Empty object of type 'SPHERE'
    bpy.ops.object.empty_add(type='SPHERE')

    # Get the active object (which should be the newly created Empty)
    empty_obj = bpy.context.active_object

    # Set the name of the Empty object
    empty_obj.name = "Rayverb - Emitter"

    # Make the name visible in the viewport
    empty_obj.show_name = True  # This ensures the name is always visible

    # Add the "is_sound_emitter" property
    empty_obj["_RNA_UI"] = empty_obj.get("_RNA_UI", {})  # Ensure _RNA_UI exists
    empty_obj["is_sound_emitter"] = 1  # Set the property to 1 (True)

    # Define how the property appears in Custom Properties
    empty_obj["_RNA_UI"]["is_sound_emitter"] = {
        "description": "Mark this Empty as a sound emitter",
        "default": 1,
        "min": 0.0,
        "max": 1.0,
        "soft_min": 0.0,
        "soft_max": 1.0
    }


def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)




emitter_count = 0

# Iterate through all objects in the current scene
for obj in bpy.context.scene.objects:
    if obj.type == 'EMPTY' and "is_sound_emitter" in obj.keys():
        emitter_count += 1

# Check if there are more than one "is_sound_emitter"
if emitter_count > 0:
    ShowMessageBox("Cannot have more than 1 emitter type object.", "Error", 'ERROR')
else:
    create_emit()








