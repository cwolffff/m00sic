"""
A module for utility functions.

"""


import random

from . import constants


OFFSET_TO_INT = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5}


# need to add get random note from input chord function 
def get_random_note_from_key(key):
    
    return random.choice(constants.NOTES_FOR_KEY[key])
    

def get_starting_note(key: str, offset: int) -> int:
    """
    Find the tonic note for the specified key, add the offset,
    and return the result.

    Returns:
        The starting note for the specified key + offset.

    """
    assert (
        offset in OFFSET_TO_INT
    ), f"Invalid offset: {offset}. Must be one of {OFFSET_TO_INT.keys()}."
    notes = constants.NOTES_FOR_KEY[key]
    tonic = constants.TONIC_NOTE_FOR_KEY[key]
    tonic_idx = notes.index(tonic)
    offset_int = OFFSET_TO_INT[offset]
    return notes[tonic_idx + offset_int]

def extract_pitches(notesequence):

    return [note.pitch for note in notesequence.notes]

def get_chord(key: str, note: int, chord: str) -> list:
    """
    Build a chord in a given key, starting from a specified note.

    """
    assert key in constants.NOTES_FOR_KEY, f"Invalid key: {key}."
    assert note in constants.NOTES_FOR_KEY[key], f"Note {note} not in key {key}."
    assert chord in constants.STEPS_FOR_CHORD, f"Invalid chord: {chord}."
    return [note + i for i in constants.STEPS_FOR_CHORD[chord]]


def get_chord_first_inversion(key: str, note: int, chord: str) -> list:
    notes = get_chord(key, note, chord)
    return notes[1:] + notes[:1]


def get_chord_second_inversion(key: str, note: int, chord: str) -> list:
    notes = get_chord(key, note, chord)
    return notes[-1:] + notes[:-1]


def build_chord_progression(key: str) -> list:
    note1 = get_starting_note(key, "I")
    chord1 = get_chord(key=key, note=note1, chord="major_triad")

    note2 = get_starting_note(key, "V")
    chord2 = get_chord_second_inversion(key=key, note=note2, chord="major_triad")

    note3 = get_starting_note(key, "VI")
    chord3 = get_chord_first_inversion(key=key, note=note3, chord="major_triad")

    note4 = get_starting_note(key, "IV")
    chord4 = get_chord_second_inversion(key=key, note=note4, chord="major_triad")

    return [chord1, chord2, chord3, chord4]


def get_random_key() -> str:
    return random.choice(constants.KEYS)

#returns the note in every octave 
def all_octaves(note):
    return [i*12+note for i in [-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7] if i*12+note >= 21 and i*12+note <= 100]