"""
A module for utility functions.
"""

import random
from typing import List
from . import constants


OFFSET_TO_INT = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5}


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


def extract_pitches(note_sequence):
    return [note.pitch for note in note_sequence.notes]


def get_chord(key: str, starting_note: int, chord: str) -> List[int]:
    """
    Build a chord in a given key, starting from a specified note.

    TODO: maybe remove key parameter?
    """
    assert key in constants.NOTES_FOR_KEY, f"Invalid key: {key}."
    assert (
        starting_note in constants.NOTES_FOR_KEY[key]
    ), f"Note {starting_note} not in key {key}."
    assert chord in constants.STEPS_FOR_CHORD, f"Invalid chord: {chord}."
    return [starting_note + i for i in constants.STEPS_FOR_CHORD[chord]]


def get_chord_first_inversion(key: str, starting_note: int, chord: str) -> List[int]:
    notes = get_chord(key, starting_note, chord)
    return sorted(notes[1:] + notes[:1])


def get_chord_second_inversion(key: str, starting_note: int, chord: str) -> List[int]:
    notes = get_chord(key, starting_note, chord)
    return sorted(notes[-1:] + notes[:-1])


def build_chord_progression(key: str) -> List[List[int]]:
    note1 = get_starting_note(key, "I")
    chord1 = get_chord(key=key, starting_note=note1, chord="major_triad")

    note2 = get_starting_note(key, "V")
    chord2 = get_chord_second_inversion(
        key=key, starting_note=note2, chord="major_triad"
    )

    note3 = get_starting_note(key, "VI")
    chord3 = get_chord_first_inversion(
        key=key, starting_note=note3, chord="major_triad"
    )

    note4 = get_starting_note(key, "IV")
    chord4 = get_chord_second_inversion(
        key=key, starting_note=note4, chord="major_triad"
    )

    return [chord1, chord2, chord3, chord4]


def get_random_key() -> str:
    return random.choice(constants.KEYS)


def all_octaves(note):
    return [
        i * 12 + note
        for i in [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]
        if i * 12 + note >= 21 and i * 12 + note <= 100
    ]
