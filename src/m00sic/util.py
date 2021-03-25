import constants


OFFSET_TO_INT = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5}


def get_starting_note(key, offset):
    """
    Find the tonic note for the specified key, add the offset,
    and return the result.

    Returns:
        (int) The starting note for the specified key + offset.
    """
    assert (
        offset in OFFSET_TO_INT
    ), f"Invalid offset: {offset}. Must be one of {OFFSET_TO_INT.keys()}."
    notes = constants.NOTES_FOR_KEY[key]
    tonic = constants.TONIC_NOTE_FOR_KEY[key]
    tonic_idx = notes.index(tonic)
    offset_int = OFFSET_TO_INT[offset]
    return notes[tonic_idx + offset_int]


def get_chord(key, note, chord):
    """
    Build a `chord` in a given `key`, starting from `note`.

    Returns:
        (list[int])
    """
    assert key in constants.NOTES_FOR_KEY, f"Invalid key: {key}."
    assert note in constants.NOTES_FOR_KEY[key], f"Note {note} not in key {key}."
    assert chord in constants.STEPS_FOR_CHORD
    return [note + i for i in constants.STEPS_FOR_CHORD[chord]]
