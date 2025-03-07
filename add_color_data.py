import bpy#type:ignore

def add_color_attribute(obj):

    if obj and obj.type == 'MESH':

        mesh = obj.data
        if "rayverb_data" not in mesh.vertex_colors:

            vertex_color_layer = mesh.vertex_colors.new(name="rayverb_data")
            print(f"Added vertex color layer to {obj.name}")
        else:
            print(f"{obj.name} already has the vertex color layer].")

obj = bpy.context.active_object  
add_color_attribute(obj)