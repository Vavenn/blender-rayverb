
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



def array_magic(time_array, energy_array, bucket_size, max_buckets):
    def sort_arrays_together(arr1, arr2):
        combined = list(zip(arr1, arr2))
        combined.sort(key=lambda x: x[0])
        sorted_arr1, sorted_arr2 = zip(*combined)
        return list(sorted_arr1), list(sorted_arr2)
    max_energy = 0
    out_array = []
    time_array, energy_array = sort_arrays_together(time_array, energy_array)
    cap = len(time_array)
    pointer_id = 0
    time_low_bound = 0
    time_max_bound = bucket_size
    nb_buckets = 0
    
    while True:
        if pointer_id >= cap or nb_buckets >= max_buckets:
            break
        total_energy = 0.0
        i = pointer_id
        while True:
            if i >= cap or time_array[i] > time_max_bound:
                break
            else:
                total_energy = total_energy + float(energy_array[i])
                i += 1
        pointer_id = i
        if abs(total_energy) > max_energy: max_energy = abs(total_energy)
        out_array.append(total_energy)
        time_low_bound += bucket_size
        time_max_bound += bucket_size
        nb_buckets += 1
    return out_array, max_energy

def export_amplitude_to_wav(amplitudes, filename, sample_rate=44100, num_channels=1):
    import wave
    import struct 
    amplitudes_flat = amplitudes
    amplitudes_int16 = [int(x * 32767) for x in amplitudes_flat]
    amplitudes_int16 = np.array(amplitudes_int16, dtype=np.int16)
    
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f'{len(amplitudes_int16)}h', *amplitudes_int16))
    print(f"File saved: {filename}")

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

MERGE_DIRECT = True

if True:
    scene = bpy.context.scene
    direct_stuff = scene.RAYVERB_direct_rays
    if debug: print("Opening File")
    file_path = file_dir+"Rayverb Data.csv" 
    remove_null_characters_from_file(file_path)
    Header, Time, Energy, Channel = parse_csv(file_path)
    if debug: print(f"Array Size:{len(Time)} | {len(Energy)} | {len(Channel)}")

    Time = [float(x)/ 343.0 for x in Time]
    trim_start = scene.RAYVERB_trim_start_silence
    if trim_start: TimeMin = float(min(Time))
    else: TimeMin = 0.0
    i = 0
    for x in Time:
        Time[i] = x - TimeMin
        i=i+1
    
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
    max_lenght = scene.RAYVERB_length_max
    samplerate = scene.RAYVERB_samplerate

    normalize_shite = False

    
    output_file = file_dir+scene.RAYVERB_output_filename+"_"
    global_max_energy = 0
    if not normalize_shite:
        for ch in range(1, CHANNELS + 1):
            wave_buffers = [0]
            ch_time = []
            for i in range(len(Channel)):
                if Channel[i] == ch:
                    ch_time.append(Time[i])
            ch_energy = []
            for i in range(len(Channel)):
                if Channel[i] == ch:
                    ch_energy.append(Energy[i])
            if not len(ch_time) == 0:
                wave_buffers, max_energy = array_magic(ch_time, ch_energy, 1/samplerate, samplerate*max_lenght)
            else:
                max_energy = 0
            if max_energy > global_max_energy: global_max_energy = max_energy



    for ch in range(1, CHANNELS + 1):
        wave_buffers = [0]
        ch_time = []
        for i in range(len(Channel)):
            if Channel[i] == ch:
                ch_time.append(Time[i])
        ch_energy = []
        for i in range(len(Channel)):
            if Channel[i] == ch:
                ch_energy.append(Energy[i])
        if not len(ch_time) == 0:
            wave_buffers, max_energy = array_magic(ch_time, ch_energy, 1/samplerate, samplerate*max_lenght)
        else:
            max_energy = 1
        if max_energy != 0:
            i = 0
            for x in wave_buffers: 
                if normalize_shite:
                    wave_buffers[i] = wave_buffers[i]/max_energy
                else:
                    wave_buffers[i] = wave_buffers[i]/global_max_energy
                i += 1
        else:
            wave_buffers = [0]
        wave_buffers = np.array(wave_buffers)
        if ch <= nb_channels:
            output_filename = output_file + Header[ch] + ".wav"
        else:
            output_filename = output_file + Header[ch-nb_channels] + "_DIRECT.wav"
        export_amplitude_to_wav(wave_buffers, output_filename , samplerate, 1)
        







