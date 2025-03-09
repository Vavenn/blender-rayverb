import bpy #type:ignore
import math
import mathutils #type:ignore
import random
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time
exit = False



def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

emitter_obj = next((eobj for eobj in bpy.context.scene.objects if eobj.type == 'EMPTY' and eobj.get("is_sound_emitter") == 1), None)
if not emitter_obj:
    ShowMessageBox("No emitter found!") # type: ignore
    exit = True



receiver_obj = next((robj for robj in bpy.context.scene.objects if robj.get("is_sound_receiver") == 1), None)
if not receiver_obj:
    ShowMessageBox("No receiver found!") # type: ignore
    exit = True

num_recievers = 0
for robj in bpy.context.scene.objects: 
    if robj.get("is_sound_receiver") != None:
        if robj.get("is_sound_receiver") > num_recievers: num_recievers = robj.get("is_sound_receiver")

labels = [0] * (0 + num_recievers)

for robj in bpy.context.scene.objects:
    id = robj.get("is_sound_receiver")
    if id != None:
        labels[id-1] = robj.name

def generate_uniform_vectors(n,rand,is_rand_on,thckness):
    import mathutils # type: ignore
    import numpy as np # type: ignore
    vectors = []
    phi = (1 + np.sqrt(5)) / 2  # Golden ratio
    for i in range(n):
        z = 1 - (2 * i) / (n - 1)  # Uniformly distributed z
        radius = np.sqrt(1 - z**2)
        theta = 2 * np.pi * i / phi  # Uniform angle using golden ratio
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        outvector = mathutils.Vector((x,y,z)).normalized()
        vectors.append(outvector)
        if is_rand_on:
            for i in range(0, thckness-1, 1):
                xa = x + np.random.uniform(-rand, rand)
                ya = y + np.random.uniform(-rand, rand)
                za = z + np.random.uniform(-rand, rand)
                outvector = mathutils.Vector((xa,ya,za)).normalized()
                vectors.append(outvector)
    return vectors

def clear_debug_lines():
    if "Ray_Debug_Lines" in bpy.data.collections:
        debug_collection = bpy.data.collections["Ray_Debug_Lines"]
        for obj in list(debug_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

def launch_rays(scene, origin, angles, max_refr_bounces, energy_threshold,inversion_chance, debug=False):
    if debug: print("Launch Rays called")
    import time
    def trace_ray(scene, origin, direction, energy, distance, refr_count, max_refr_bounces, 
                energy_threshold, results, dgraph, inversion_chance, is_direct, debug=False):
        import random
        def draw_debug_line(start, end, hit_receiver=False):

            if "Ray_Debug_Lines" not in bpy.data.collections:
                debug_collection = bpy.data.collections.new("Ray_Debug_Lines")
                bpy.context.scene.collection.children.link(debug_collection)
            else:
                debug_collection = bpy.data.collections["Ray_Debug_Lines"]

            mesh = bpy.data.meshes.new(name="Ray_Line")
            obj = bpy.data.objects.new(name="Ray_Line", object_data=mesh)
            debug_collection.objects.link(obj)

            mesh.from_pydata([start, end], [(0, 1)], [])
            mesh.update()

            mat = bpy.data.materials.get("RayMaterial")
            if not mat:
                mat = bpy.data.materials.new(name="RayMaterial")
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs[0].default_value = (1, 1, 1, 1)  # White

            mat.diffuse_color = (1, 0, 0, 1) if hit_receiver else (1, 1, 1, 1)
            obj.data.materials.append(mat)

        def get_material_properties(obj):

            default_reflection = 0.97
            default_transmission = 0.15
            default_randomness = 0.0

            if obj.data and "rayverb_data" in obj.data.attributes:
                attr = obj.data.attributes["rayverb_data"]
                if attr.data and len(attr.data) > 0:
                    color = attr.data[0].color
                    return color[0], color[1], color[2]

            return default_reflection, default_transmission, default_randomness

        def add_randomness(vector, randomness):

            import mathutils # type:ignore
            import math
            import random
            if randomness > 0:
                max_angle = randomness * 0.1 * math.pi  # ±10% variation in angle
                angle_x = random.uniform(-max_angle, max_angle)
                angle_y = random.uniform(-max_angle, max_angle)

                rot_x = mathutils.Matrix.Rotation(angle_x, 3, 'X')
                rot_y = mathutils.Matrix.Rotation(angle_y, 3, 'Y')

                return (rot_x @ rot_y @ vector).normalized()
            
            return vector

        def compute_refraction_direction(direction, normal, obj, randomness):
            import math
            ior = obj.get("ior", 1.5)  # Default IOR if not specified
            cosi = max(-1.0, min(1.0, direction.dot(normal)))  # Clamped cosine
            entering = cosi < 0  # True if entering material
            etai, etat = (1.0, ior) if entering else (ior, 1.0)  # Swap IORs based on direction
            normal = normal if entering else -normal  # Flip normal if exiting

            eta = etai / etat
            k = 1 - eta * eta * (1 - cosi * cosi)

            if k < 0:
                return None  # Total internal reflection (TIR) occurs

            refracted_dir = eta * direction + (eta * cosi - math.sqrt(k)) * normal
            return add_randomness(refracted_dir.normalized(), randomness)

        if abs(energy) < energy_threshold:
            return

        hit, hit_location, hit_normal, _, hit_object, _ = scene.ray_cast(dgraph, origin, direction)

        if not hit:
            return  # No intersection, terminate ray


            

        travel_distance = (hit_location - origin).length
        distance += travel_distance

        receiver_id = hit_object.get("is_sound_receiver")
        if receiver_id is not None:
            #print(receiver_id)
            if is_direct: receiver_id = -int(receiver_id) 
            results.append((distance, energy, int(receiver_id)))
            if debug:
                draw_debug_line(origin, hit_location, hit_receiver=True)  # Red for receiver hit
            return

        is_direct = False

        if debug:
            draw_debug_line(origin, hit_location, hit_receiver=False)  # White for normal rays

        reflection_coeff, transmission_coeff, randomness = get_material_properties(hit_object)

        bounce_sum = reflection_coeff + transmission_coeff
        if bounce_sum > 1:
            reflection_coeff = reflection_coeff/bounce_sum
            transmission_coeff = transmission_coeff/bounce_sum

        if random.uniform(0, 1) < inversion_chance:
            energy = -energy

        reflected_energy = energy * reflection_coeff
        if abs(reflected_energy) > energy_threshold:
            reflected_dir = direction - 2 * direction.dot(hit_normal) * hit_normal
            reflected_dir = add_randomness(reflected_dir, randomness)
            trace_ray(scene, hit_location + reflected_dir * 0.001, reflected_dir.normalized(), 
                    reflected_energy, distance, refr_count, max_refr_bounces, energy_threshold, results, dgraph,inversion_chance,is_direct,debug)

        if refr_count < max_refr_bounces and transmission_coeff > 0:
            refracted_energy = energy * transmission_coeff
            if refracted_energy > energy_threshold:
                refracted_dir = compute_refraction_direction(direction, hit_normal, hit_object, randomness)
                if refracted_dir:
                    trace_ray(scene, hit_location + refracted_dir * 0.001, refracted_dir.normalized(), 
                            refracted_energy, distance, refr_count + 1, max_refr_bounces, energy_threshold, results, dgraph,inversion_chance,is_direct, debug)
    depsgraph = bpy.context.evaluated_depsgraph_get() 
    results = []
    i = 0 
    progress_chunk = len(angles)/(100)
    j = 0
    prev = 0
    pre_len = 0
    starttime = time.time()
    for angle in angles:
        direction = angle
        
        args = (scene, origin, direction, 100.0, 0.0, 0, max_refr_bounces, energy_threshold, results, depsgraph,inversion_chance,True, debug )
        trace_ray(*args)
        
        if i > j:
            pre_len = len(results)-prev
            time_estimate = ((time.time()-starttime)/i)*(len(angles)-i)
            if 5 - len(str(pre_len)) >= 0: display_pre_len = (5 - len(str(pre_len)))*" "+str(pre_len)
            else: display_pre_len = pre_len
            if 4 - len(str(round(100*i/len(angles),1))) >= 0: display_prog = (4 - len(str(round(100*i/len(angles),1))))*" "+str(round(100*i/len(angles),1))
            else: display_prog = round(100*i/len(angles),1)
            print(f"Progress: {display_prog}%  |  New: {display_pre_len}  |  ETA: {round(time_estimate,1)}s")
            j += progress_chunk
            prev = len(results)
        i += 1
    delta_t = time.time() - starttime
    return results, delta_t

if not exit:

    prefs = bpy.context.preferences.addons[__name__].preferences
    data_output_path = prefs.RAYVERB_data_output

    print("Data Output Path: ", data_output_path)
    scene = bpy.context.scene



    origin = mathutils.Vector(emitter_obj.location)
    rng_on = scene.RAYVERB_ray_thickness_on
    max_it = scene.RAYVERB_ray_amount
    ray_thickness = scene.RAYVERB_ray_thickness

    if rng_on:
        max_it = round(max_it/ray_thickness)
        real_max = max_it*ray_thickness
    else:
        real_max = max_it

    angles = generate_uniform_vectors(max_it,0.05,rng_on,ray_thickness) 
    max_refr_bounces = scene.RAYVERB_refraction_max
    energy_threshold = scene.RAYVERB_energy_thresold
    debug = False  # Enable visualization
    inversion_chance = 1  # 50% chance to invert energy on reflection


    clear_debug_lines()

    ray_results, timetaken = launch_rays(scene, origin, angles, max_refr_bounces, energy_threshold, inversion_chance, debug)

    total_energy = 0
    for data in ray_results:
        total_energy += data[1]

    print(f"Done! Rays sent: {len(angles)}, lost {round(100*(1-total_energy/(100*len(angles))),2)}%")
    print(f"Time taken: {time.strftime('%H:%M:%S',time.gmtime(timetaken))}, about {time.strftime('%H:%M:%S',time.gmtime(1000000*timetaken/len(angles)))} per million ray")
    file_out = data_output_path+"Rayverb Data.csv"
    file_header = ""
    for label in labels:
        file_header += ";" + str(label)

    with open(file_out, "w") as out_file:
        np.savetxt(out_file, ray_results, delimiter=';', fmt='%.6f', comments='', header=file_header) 
        print(f"Data saved at: {file_out}")
