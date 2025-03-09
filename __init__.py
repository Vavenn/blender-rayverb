import os
import bpy# type:ignore
import numpy as np

bl_info = {
    "name": "Rayverb",
    "blender": (3, 0, 0),
    "category": "Object",
}

def run_add_emitter(self, context):
    with open(os.path.join(os.path.dirname(__file__), "create_emitter.py")) as f:
        exec(f.read())

def run_add_reciever(self, context):
    with open(os.path.join(os.path.dirname(__file__), "create_reciever.py")) as f:
        exec(f.read())

def run_raysim(self, context):
    with open(os.path.join(os.path.dirname(__file__), "ray_sim.py")) as f:
        exec(f.read())

def run_add_data(self, context):
    with open(os.path.join(os.path.dirname(__file__), "add_color_data.py")) as f:
        exec(f.read())
        
def run_compile_data(self, context):
    with open(os.path.join(os.path.dirname(__file__), "csv recompile to wav blender.py")) as f:
        exec(f.read())
    
def run_increment_data(self,context):
    with open(os.path.join(os.path.dirname(__file__), "increment_data.py")) as f:
        exec(f.read())

def run_visualize_receiver_data(self,context):
    with open(os.path.join(os.path.dirname(__file__), "visualize_receiver_data.py")) as f:
        exec(f.read())

def register_properties():
    bpy.types.Scene.RAYVERB_ray_amount = bpy.props.IntProperty(
        name="Ray Amount",
        description="Number of rays to be sent.",
        default=100000,
        min=2,
    )
    bpy.types.Scene.RAYVERB_ray_thickness = bpy.props.IntProperty(
        name="Ray Thickness",
        description="Groups of X rays will be grouped up tightly. Does not affect the total number of rays sent.",
        default=0,
        min=0,
    )
    bpy.types.Scene.RAYVERB_ray_thickness_on = bpy.props.BoolProperty(
        name="Ray Thickness Enabled",
        description="Enable / Disable thickness",
        default=False
    )
    bpy.types.Scene.RAYVERB_refraction_max = bpy.props.IntProperty(
        name="Refraction Max Count",
        description="Maximum number of times a ray can emit refraction.",
        default=3,
        min=0,
    )
    bpy.types.Scene.RAYVERB_energy_thresold = bpy.props.FloatProperty(
        name="Energy Thresold",
        description="Thresold for killing rays.",
        default=1.0,
        min=0.0,
        max=100.0
    )
    bpy.types.Scene.RAYVERB_samplerate = bpy.props.IntProperty(
        name="Samplerate",
        description="Samplerate for the output file.",
        default=44100,
        min=1,
    )
    bpy.types.Scene.RAYVERB_length_max = bpy.props.IntProperty(
        name="Max Length",
        description="Maximum lenght of output file, in seconds.",
        default=10,
        min=1,
    )
    bpy.types.Scene.RAYVERB_trim_start_silence = bpy.props.BoolProperty(
        name="Trim Silence",
        description="Trims the silence before the global first hit.",
        default=True
    )
    bpy.types.Scene.RAYVERB_direct_rays = bpy.props.EnumProperty(
        name="Direct rays processing",
        description="Different ways to save direct rays.",
        items=[
        ('OMIT', "Omit", "Omit direct hits."),
        ('MERGE', "Merge", "Merges direct hits with reflected hits."),
        ('SEPARATE', "Separate", "Outputs direct hits into separate files."),
        ],
        default='OMIT'
    )
    bpy.types.Scene.RAYVERB_output_filename = bpy.props.StringProperty(
        name="Output file name",
        description="Name for output files (without extension)",
        default="Rayverb_out",
    )

def unregister_properties():
    del bpy.types.Scene.RAYVERB_ray_amount
    del bpy.types.Scene.RAYVERB_ray_thickness
    del bpy.types.Scene.RAYVERB_ray_thickness_on
    del bpy.types.Scene.RAYVERB_refraction_max
    del bpy.types.Scene.RAYVERB_energy_thresold
    del bpy.types.Scene.RAYVERB_samplerate
    del bpy.types.Scene.RAYVERB_length_max
    del bpy.types.Scene.RAYVERB_trim_start_silence
    del bpy.types.Scene.RAYVERB_direct_rays
    del bpy.types.Scene.RAYVERB_output_filename


class RAYVERB_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.split('.')[-1]

    RAYVERB_data_output: bpy.props.StringProperty(
        name="Data output location",
        description="File path for measured data, in CSV format",
        default="",
        subtype='DIR_PATH'
    )#type:ignore

    def draw(self, context):
        layout = self.layout
        layout.label(text="Global Settings", icon='PREFERENCES')
        layout.prop(self, "RAYVERB_data_output")

class SCRIPT_add_emitter(bpy.types.Operator):
    bl_idname = "script.createemitter"
    bl_label = "Add Emitter to scene"

    def execute(self, context):
        run_add_emitter(self, context)
        return {'FINISHED'}

class SCRIPT_add_reciever(bpy.types.Operator):
    bl_idname = "script.createreciever"
    bl_label = "Add Receiver to scene"

    def execute(self, context):
        run_add_reciever(self, context)
        return {'FINISHED'}

class SCRIPT_start_raysim(bpy.types.Operator):
    bl_idname = "script.raysim"
    bl_label = "Ray simulation"

    def execute(self, context):
        run_raysim(self, context)
        return {'FINISHED'}
    
class SCRIPT_increment_data(bpy.types.Operator):
    bl_idname = "script.increment_data"
    bl_label = "Increment Data"

    def execute(self, context):
        run_increment_data(self, context)
        return {'FINISHED'}
    
class SCRIPT_add_data(bpy.types.Operator):
    bl_idname = "script.add_data"
    bl_label = "Add color data to selected."
    bl_description = "Adds the appropriate vertex color layer to selection.\nColor channels are mapped to:\n  R - Reflection itnensity\n  G - Refraction intensity\n  B - Collision randomness\n  A - Currently unused\n \nIf no vertex color data is present, default predefined vales are used"
    

    def execute(self, context):
        run_add_data(self, context)
        return {'FINISHED'}

class SCRIPT_recompile_data(bpy.types.Operator):
    bl_idname = "script.recompile_data"
    bl_label = "The funky stuff."

    def execute(self, context):
        run_compile_data(self, context)
        return {'FINISHED'}

class SCRIPT_visualize_reciever_data(bpy.types.Operator):
    bl_idname = "script.visualize_receiver_data"
    bl_label = "The funky stuff."

    def execute(self, context):
        run_visualize_receiver_data(self, context)
        return {'FINISHED'}

class RAYVERB_export_panel(bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "OBJECT_PT_rayverb_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rayverb"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="Output file name prefix:")
        layout.prop(scene, "RAYVERB_output_filename", text="")
        layout.separator()

        stuffgroup = layout.box()
        labeltextrow = stuffgroup.row()
        labeltextrow.label(text="")
        labeltextrow.label(text="Parameters")
        labeltextrow.label(text="")
        stuffgroup.prop(scene, "RAYVERB_samplerate")
        randomrow = stuffgroup.row()
        randomrow.prop(scene, "RAYVERB_length_max")
        randomrow.prop(scene, "RAYVERB_trim_start_silence")
        direct_row = stuffgroup.row()
        direct_row.label(text="Direct rays:")
        direct_row.prop(scene, "RAYVERB_direct_rays", text="")
        layout.separator()
        extrarow = layout.row()
        extrarow.operator("script.visualize_receiver_data", text="Visualize Data")
        layout.separator()
        layout.separator()
        export_start_box = layout.box()
        export_start_box_inthebox = export_start_box.box()
        export_start_box_inthebox.operator("script.recompile_data", text="Export to WAV")

class RAYVERB_main_panel(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "OBJECT_PT_rayverb_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rayverb"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        addon_prefs = bpy.context.preferences.addons.get(__name__.split('.')[-1])
        prefs = addon_prefs.preferences if addon_prefs else None

        layout.separator()
        row = layout.row()
        row.operator("script.createemitter", text="Create Emitter", icon='LIGHT')
        row.operator("script.createreciever", text="Create Receiver", icon='CAMERA_DATA')
        extrarow = layout.row()
        extrarow.operator("script.increment_data", text="Increment Reciever ID")


        layout.separator()
        ray_settings_box = layout.box()
        col = ray_settings_box.row()
        col.alignment = 'CENTER'
        col.separator()
        col.label(text="Ray Properties")
        col.separator()
        ray_settings_box.prop(scene, "RAYVERB_ray_amount", text="Amount")
        thickness_row = ray_settings_box.row()
        thickness_row.prop(scene, "RAYVERB_ray_thickness_on", text="")
        thickness_row.prop(scene, "RAYVERB_ray_thickness", text="Thickness")
        ray_settings_box.prop(scene, "RAYVERB_refraction_max", text="Max Number of Refractions")
        ray_settings_box.prop(scene, "RAYVERB_energy_thresold", text="Energy thresold")
        
        layout.separator()

        layout.operator("script.add_data",text="Add Color Data to selection")


        layout.separator()
        layout.label(text="Data saving path")
        if prefs:
            layout.prop(prefs, "RAYVERB_data_output",text="")
        layout.separator()
        layout.separator()
        export_start_box = layout.box()
        export_start_box_inthebox = export_start_box.box()
        export_start_box_inthebox.operator("script.raysim", text="Run Simulation")

classes = [
    RAYVERB_AddonPreferences,
    SCRIPT_add_emitter,
    SCRIPT_add_reciever,
    SCRIPT_start_raysim,
    RAYVERB_main_panel,
    RAYVERB_export_panel,
    SCRIPT_add_data,
    SCRIPT_increment_data,
    SCRIPT_visualize_reciever_data,
    SCRIPT_recompile_data
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()

if __name__ == "__main__":
    register()
