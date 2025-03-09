from pickle import FALSE
import numpy as np


from itertools import zip_longest
import bpy#type:ignore


prefs = bpy.context.preferences.addons[__name__].preferences
file_dir = prefs.RAYVERB_data_output



debug = False
if debug: print("Start")

def flatten_by_index(nested_lists):
    return [item for group in zip_longest(*nested_lists, fillvalue=0) for item in group]

def find_indices_in_range(arr, min_val, max_val):
    indices = [i for i, x in enumerate(arr) if min_val <= x <= max_val]
    return indices

def remove_null_characters_from_file(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    cleaned_content = content.replace(b'\x00', b'')
    with open(file_path, 'wb') as file:
        file.write(cleaned_content)

def parse_csv(file_path):
    import csv
    column1, column2, column3 = [], [], []
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        header = next(reader, None)  # Read the header row
        for row in reader:
            if len(row) == 3:
                column1.append(row[0])
                column2.append(row[1])
                column3.append(row[2])
    return header, column1, column2, column3

def count_numbers(lst):
    counts = {}
    for num in lst:
        counts[num] = counts.get(num, 0) + 1
    return counts

if True:
    scene = bpy.context.scene
    direct_stuff = scene.RAYVERB_direct_rays
    if debug: print("Opening File")
    file_path = file_dir+"Rayverb Data.csv" 
    remove_null_characters_from_file(file_path)
    Header, _, Energy, Channel = parse_csv(file_path)
    Energy = [float(x) for x in Energy]
    Channel = [round(float((x))) for x in Channel]
    nb_channels = max(Channel)
    if True:
        NewChannel=Channel
        i = 0
        for x in Channel:
            if x < 0: 
                if direct_stuff == "MERGE": NewChannel[i] = abs(x)
                elif direct_stuff == "SEPARATE": NewChannel[i] = abs(x) + nb_channels
                else: NewChannel[i] = 0
            elif x >= 0: NewChannel[i] = x
            i += 1
    Channel = [round(float((x))) for x in NewChannel]

    CHANNELS = max(Channel)
    results_channel = []
    results_energy = []
    max_label_lenght = 0
    global_max_energy = 0
    for ch in range(1, CHANNELS + 1):
        channel_energy = 0
        for i in range(len(Channel)):
            if Channel[i] == ch:
                channel_energy += Energy[i]
        channel_energy = abs(channel_energy)
        if channel_energy>global_max_energy: global_max_energy = channel_energy
        results_channel.append(ch)
        results_energy.append(channel_energy)
        if len(Header[ch]) > max_label_lenght: max_label_lenght = len(Header[ch])
        #print(f"{Header[ch]}: {channel_energy}")

fill_char="■"
for ch in results_channel:
    label = Header[ch]
    spacer = ""
    if len(label) < max_label_lenght: spacer = " "*(max_label_lenght-len(label))
    nrj = results_energy[ch-1]/global_max_energy
    outstring = spacer+round(nrj*100)*fill_char
    print(f"{label}: {outstring}")



                
    


