import bpy #type:ignore

def create_emit():
    bpy.ops.object.empty_add(type='SPHERE')
    empty_obj = bpy.context.active_object
    empty_obj.name = "Rayverb - Emitter"
    empty_obj.show_name = True 
    empty_obj["_RNA_UI"] = empty_obj.get("_RNA_UI", {}) 
    empty_obj["is_sound_emitter"] = 1  

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

for obj in bpy.context.scene.objects:
    if obj.type == 'EMPTY' and "is_sound_emitter" in obj.keys():
        emitter_count += 1
if emitter_count > 0:
    ShowMessageBox("Cannot have more than 1 emitter type object.", "Error", 'ERROR')
else:
    create_emit()








