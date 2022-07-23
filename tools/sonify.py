'''
MIT License

Copyright (c) 2017 Erin Braswell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import io
from time import sleep

from pretty_midi import note_name_to_number
from midiutil.MidiFile import MIDIFile

NOTES = [
    ['C'], ['C#', 'Db'], ['D'], ['D#', 'Eb'], ['E'], ['F'], ['F#', 'Gb'],
    ['G'], ['G#', 'Ab'], ['A'], ['A#', 'Bb'], ['B']
]

def get_keys():
    base_keys = {
        'c_major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'd_major': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
        'e_major': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
        'f_major': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E', 'F'],
        'g_major': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
        'a_major': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#', 'A'],
        'b_major': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#', 'B'],
        'c_sharp_major': ['Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C', 'Db'],
        'd_sharp_major': ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D'],
        'f_sharp_major': ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'F', 'F#'],
        'g_sharp_major': ['Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G', 'Ab'],
        'a_sharp_major': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A', 'Bb']
    }

    base_keys['d_flat_major'] = base_keys['c_sharp_major']
    base_keys['e_flat_major'] = base_keys['d_sharp_major']
    base_keys['g_flat_major'] = base_keys['f_sharp_major']
    base_keys['a_flat_major'] = base_keys['g_sharp_major']
    base_keys['b_flat_major'] = base_keys['a_sharp_major']

    return base_keys


KEYS = get_keys()

# Instrument and Percussion map from
# https://www.midi.org/specifications/item/gm-level-1-sound-set

INSTRUMENTS = {
    'accordion': 22,
    'acoustic bass': 33,
    'acoustic grand piano': 1,
    'acoustic guitar (nylon)': 25,
    'acoustic guitar (steel)': 26,
    'agogo': 114,
    'alto sax': 66,
    'applause': 127,
    'bagpipe': 110,
    'banjo': 106,
    'baritone sax': 68,
    'bassoon': 71,
    'bird tweet': 124,
    'blown bottle': 77,
    'brass section': 62,
    'breath noise': 122,
    'bright acoustic piano': 2,
    'celesta': 9,
    'cello': 43,
    'choir aahs': 53,
    'church organ': 20,
    'clarinet': 72,
    'clavi': 8,
    'contrabass': 44,
    'distortion guitar': 31,
    'drawbar organ': 17,
    'dulcimer': 16,
    'electric bass (finger)': 34,
    'electric bass (pick)': 35,
    'electric grand piano': 3,
    'electric guitar (clean)': 28,
    'electric guitar (jazz)': 27,
    'electric guitar (muted)': 29,
    'electric piano 1': 5,
    'electric piano 2': 6,
    'english horn': 70,
    'fiddle': 111,
    'flute': 74,
    'french horn': 61,
    'fretless bass': 36,
    'fx 1 (rain)': 97,
    'fx 2 (soundtrack)': 98,
    'fx 3 (crystal)': 99,
    'fx 4 (atmosphere)': 100,
    'fx 5 (brightness)': 101,
    'fx 6 (goblins)': 102,
    'fx 7 (echoes)': 103,
    'fx 8 (sci-fi)': 104,
    'glockenspiel': 10,
    'guitar fret noise': 121,
    'guitar harmonics': 32,
    'gunshot': 128,
    'harmonica': 23,
    'harpsichord': 7,
    'helicopter': 126,
    'honky-tonk piano': 4,
    'kalimba': 109,
    'koto': 108,
    'lead 1 (square)': 81,
    'lead 2 (sawtooth)': 82,
    'lead 3 (calliope)': 83,
    'lead 4 (chiff)': 84,
    'lead 5 (charang)': 85,
    'lead 6 (voice)': 86,
    'lead 7 (fifths)': 87,
    'lead 8 (bass + lead)': 88,
    'marimba': 13,
    'melodic tom': 118,
    'music box': 11,
    'muted trumpet': 60,
    'oboe': 69,
    'ocarina': 80,
    'orchestra hit': 56,
    'orchestral harp': 47,
    'overdriven guitar': 30,
    'pad 1 (new age)': 89,
    'pad 2 (warm)': 90,
    'pad 3 (polysynth)': 91,
    'pad 4 (choir)': 92,
    'pad 5 (bowed)': 93,
    'pad 6 (metallic)': 94,
    'pad 7 (halo)': 95,
    'pad 8 (sweep)': 96,
    'pan flute': 76,
    'percussive organ': 18,
    'piccolo': 73,
    'pizzicato strings': 46,
    'recorder': 75,
    'reed organ': 21,
    'reverse cymbal': 120,
    'rock organ': 19,
    'seashore': 123,
    'shakuhachi': 78,
    'shamisen': 107,
    'shanai': 112,
    'sitar': 105,
    'slap bass 1': 37,
    'slap bass 2': 38,
    'soprano sax': 65,
    'steel drums': 115,
    'string ensemble 1': 49,
    'string ensemble 2': 50,
    'synth bass 1': 39,
    'synth bass 2': 40,
    'synth drum': 119,
    'synth voice': 55,
    'synthbrass 1': 63,
    'synthbrass 2': 64,
    'synthstrings 1': 51,
    'synthstrings 2': 52,
    'taiko drum': 117,
    'tango accordion': 24,
    'telephone ring': 125,
    'tenor sax': 67,
    'timpani': 48,
    'tinkle bell': 113,
    'tremolo strings': 45,
    'trombone': 58,
    'trumpet': 57,
    'tuba': 59,
    'tubular bells': 15,
    'vibraphone': 12,
    'viola': 42,
    'violin': 41,
    'voice oohs': 54,
    'whistle': 79,
    'woodblock': 116,
    'xylophone': 14
}

PERCUSSION = {
    'acoustic bass drum': 35,
    'acoustic snare': 38,
    'bass drum 1': 36,
    'cabasa': 69,
    'chinese cymbal': 52,
    'claves': 75,
    'closed hi hat': 42,
    'cowbell': 56,
    'crash cymbal 1': 49,
    'crash cymbal 2': 57,
    'electric snare': 40,
    'hand clap': 39,
    'hi bongo': 60,
    'hi wood block': 76,
    'hi-mid tom': 48,
    'high agogo': 67,
    'high floor tom': 43,
    'high timbale': 65,
    'high tom': 50,
    'long guiro': 74,
    'long whistle': 72,
    'low agogo': 68,
    'low bongo': 61,
    'low conga': 64,
    'low floor tom': 41,
    'low timbale': 66,
    'low tom': 45,
    'low wood block': 77,
    'low-mid tom': 47,
    'maracas': 70,
    'mute cuica': 78,
    'mute hi conga': 62,
    'mute triangle': 80,
    'open cuica': 79,
    'open hi conga': 63,
    'open hi-hat': 46,
    'open triangle': 81,
    'pedal hi-hat': 44,
    'ride bell': 53,
    'ride cymbal 1': 51,
    'ride cymbal 2': 59,
    'short guiro': 73,
    'short whistle': 71,
    'side stick': 37,
    'splash cymbal': 55,
    'tambourine': 54,
    'vibraslap': 58
}


def make_first_number_match_key(y_values, notes_in_key):
    first_note_in_key = notes_in_key[0]
    transpose_value = first_note_in_key - y_values[0]
    new_y = []
    for y in y_values:
        new_y.append(y + transpose_value)

    return new_y


def convert_to_key(data, key, number_of_octaves=4):
    instrument, instrument_type = None, None
    if type(data[0]) != tuple:
        instrument = data.pop(0)
        _, instrument_type = get_instrument(instrument)

    x, y, z = zip(*data)

    if instrument_type == 'percussion':
        new_y = y
    else:
        # Finding the index of the note closest to all the notes in the options list
        notes_in_key = key_name_to_notes(key, number_of_octaves=number_of_octaves)

        transposed_y = make_first_number_match_key(y, notes_in_key)
        scaled_y = scale_list_to_range(transposed_y, new_min=min(notes_in_key), new_max=max(notes_in_key))

        new_y = []
        for note in scaled_y:
            new_y.append(get_closest_midi_value(note, notes_in_key))

    processed_data = list(zip(x, new_y, z))

    if instrument:
        processed_data = [instrument] + processed_data

    return processed_data


def key_name_to_notes(key, octave_start=1, number_of_octaves=4):
    """ Convert a key name to notes, using C3=60
    :param key: String matching one of the values in pre-defined KEY dict
    :param octave_start: octave for the first note, as defined by C3=60
    :param number_of_octaves: The number of octaves to include in the list
    :return:
    """
    key = KEYS.get(key)
    if not key:
        raise ValueError('No key by that name found')

    notes = []
    octave = octave_start + 1
    while len(notes) < number_of_octaves * 7:
        for note in key:
            note_with_octave = note + str(octave)
            note_number = note_name_to_number(note_with_octave)
            if note_number % 12 == 0 and len(notes) != 0:
                octave += 1
                note_with_octave = note + str(octave)
                note_number = note_name_to_number(note_with_octave)
            notes.append(note_number)

    return notes


def get_closest_midi_value(value, possible_values):
    return sorted(possible_values, key=lambda i: abs(i - value))[0]


def scale_y_to_midi_range(data, new_min=0, new_max=127):
    """
    midi notes have a range of 0 - 127. Make sure the data is in that range
    data: list of tuples of x, y coordinates for pitch and timing
    min: min data value, defaults to 0
    max: max data value, defaults to 127
    return: data, but y normalized to the range specified by min and max
    """
    if new_min < 0 or new_max > 127:
        raise ValueError('Midi notes must be in a range from 0 - 127')

    x, y = zip(*data)
    new_y = scale_list_to_range(y, new_min, new_max)

    return list(zip(x, new_y))


def scale_list_to_range(list_to_scale, new_min, new_max):
    old_min = min(list_to_scale)
    old_max = max(list_to_scale)
    return [get_scaled_value(value, old_min, old_max, new_min, new_max) for value in list_to_scale]


def get_scaled_value(old_value, old_min, old_max, new_min, new_max):
    return ((old_value - old_min)/(old_max - old_min)) * (new_max - new_min) + new_min


def quantize_x_value(list_to_quantize, steps=0.5):
    # Restrict the x range to something that's a  multiple of the number of steps given!
    quantized_x = []
    for x in list_to_quantize:
        quantized_x.append(round(steps * round(float(x) / steps), 2))
    return quantized_x


def get_instrument(instrument_name):
    instrument_type = 'melodic'
    program_number = INSTRUMENTS.get(instrument_name.lower())
    if not program_number:
        program_number = PERCUSSION.get(instrument_name.lower())
        instrument_type = 'percussion'
        if not program_number:
            raise AttributeError('No instrument or percussion could be found by that name')
    return program_number - 1, instrument_type


def write_to_midifile(data, track_type='single'):
    """
    data: list of tuples of x, y coordinates for pitch and timing
          Optional: add a string to the start of the data list to specify instrument!
    type: the type of data passed to create tracks. Either 'single' or 'multiple'
    """
    if track_type not in ['single', 'multiple']:
        raise ValueError('Track type must be single or multiple')

    if track_type == 'single':
        data = [data]

    memfile = io.BytesIO()
    midifile = MIDIFile(numTracks=len(data), adjust_origin=False)

    track = 0
    time = 0
    program = 0
    channel = 0
    duration = 1
    volume = 80
    tempo=300

    for data_list in data:
        midifile.addTrackName(track, time, 'Track {}'.format(track))
        midifile.addTempo(track, time, 300)

        instrument_type = 'melodic'
        if type(data_list[0]) != tuple:
            program, instrument_type = get_instrument(data_list.pop(0))

        if instrument_type == 'percussion':
            volume = 100
            channel = 9

        # Write the notes we want to appear in the file
        for point in data_list:
            time = point[0]
            duration=point[1]
            pitch = int(point[1]) if instrument_type == 'melodic' else program
            midifile.addNote(track, channel, pitch, time, duration, volume)
            midifile.addProgramChange(track, channel, time, program)

        track += 1
        channel = 0

    midifile.writeFile(memfile)

    return memfile



def create_midi_from_data(input_data, outputfile="myfile.midi", key=None, number_of_octaves=4, track_type='single'):
    """
    input_data: a list of tuples, or a list of lists of tuples to add as separate tracks
    eg:
    input_data = [(1, 5), (5, 7)] OR
    input_data = [
        [(1, 5), (5, 7)],
        [(4, 7), (2, 10)]
    ]
    key: key to play back the graph -- see constants.py for current choices
    number_of_octaves: number of octaves used to restrict the music playback
     when converting to a key
    optional -- append an instrument name to the start of each data list
                to play back using that program number!
    """
    if key:
        if track_type == 'multiple':
            data = []
            for data_list in input_data:
                data.append(convert_to_key(data_list, key, number_of_octaves))
        else:
            data = convert_to_key(input_data, key, number_of_octaves)
    else:
        data = input_data

    memfile = write_to_midifile(data, track_type)
    with open(outputfile, "wb") as outfile:
    	 outfile.write(memfile.getbuffer())


