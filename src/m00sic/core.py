"""Core classes and methods.

Nomenclature:
- A note SYMBOL is a combination of a letter and, optionally, an accidental, e.g. 'A#'.
- A note NAME is a note symbol followed by an octave, e.g. 'A#4'.
- The RANK of a note is an integer that indicates its position within its octave. It's
always between 0 and 11.

"""


import re
from dataclasses import dataclass, field
from typing import List


SYMBOL_NAMES = [
    ("C"),
    ("C#", "Db"),
    ("D"),
    ("D#", "Eb"),
    ("E"),
    ("F"),
    ("F#", "Gb"),
    ("G"),
    ("G#", "Ab"),
    ("A"),
    ("A#", "Bb"),
    ("B"),
]
VALID_SYMBOL_NAMES = [
    symbol for symbol_tuple in SYMBOL_NAMES for symbol in symbol_tuple
]
_SYMBOL_NAME_TO_RANK = {
    symbol: rank
    for rank, symbol_tuple in enumerate(SYMBOL_NAMES)
    for symbol in symbol_tuple
}


_C0_MIDI_NUM = 12
LOWEST_PIANO_MIDI_NUM = 21  # A0
HIGHEST_PIANO_MIDI_NUM = 108  # C8


LOWEST_PIANO_OCTAVE = 0
HIGHEST_PIANO_OCTAVE = 8
NOTES_PER_OCTAVE = 12


def _get_octave(midi_num):
    return (midi_num - _C0_MIDI_NUM) // NOTES_PER_OCTAVE


def _get_rank(midi_num):
    return (midi_num - _C0_MIDI_NUM) % NOTES_PER_OCTAVE


def _to_note_name(midi_num):
    assert midi_num >= _C0_MIDI_NUM
    octave = _get_octave(midi_num)
    rank = _get_rank(midi_num)
    symbol_names = SYMBOL_NAMES[rank]
    return f"{symbol_names[0]}{octave}"


def _to_midi_num(symbol_name, octave):
    rank = _SYMBOL_NAME_TO_RANK[symbol_name]
    return _C0_MIDI_NUM + NOTES_PER_OCTAVE * octave + rank


def _get_trailing_number(s):
    m = re.search(r"\d+$", s)
    return m.group() if m else None


@dataclass
class Symbol:
    """A musical symbol, e.g. 'G#' or 'B'."""

    name: str
    index: int = field(init=False)

    def __post_init__(self):
        assert self.name in VALID_SYMBOL_NAMES
        for i, symbol_tuple in enumerate(SYMBOL_NAMES):
            if self.name in symbol_tuple:
                self.index = i
                return
        raise ValueError(f"Invalid symbol name: {self.name}")

    def __add__(self, other):
        if not isinstance(other, int):
            raise TypeError(
                f"Can only add integers to Symbol object, not type {type(other)}."
            )
        new_index = (self.index + other) % NOTES_PER_OCTAVE
        new_name = SYMBOL_NAMES[new_index][0]
        return Symbol(new_name)

    def __sub__(self, other):
        if not isinstance(other, int):
            raise TypeError(
                f"Can only subtract integers from Symbol object, not type {type(other)}."
            )
        return self.__add__(-other)


class Note:
    def __init__(self, name):
        """
        Args:
            name: e.g. 'A5', 'C#4', or 'Gb3'.
        """
        # Check if octave is valid.
        octave = _get_trailing_number(name)
        assert octave is not None, f"Invalid note name: {name}. Must contain octave."
        octave_nchar = len(octave)
        octave = int(octave)
        assert LOWEST_PIANO_OCTAVE <= octave <= HIGHEST_PIANO_OCTAVE

        # Check if note name is valid.
        symbol_name = name[:-octave_nchar]
        assert symbol_name in VALID_SYMBOL_NAMES

        self.name = name
        self.symbol = Symbol(symbol_name)
        self.octave = octave
        self.midi_num = _to_midi_num(symbol_name, octave)

    @classmethod
    def from_midi_num(cls, midi_num):
        assert LOWEST_PIANO_MIDI_NUM <= midi_num <= HIGHEST_PIANO_MIDI_NUM
        name = _to_note_name(midi_num)
        return cls(name)

    def __add__(self, other):
        if not isinstance(other, int):
            raise TypeError(
                f"Can only add integers to Note object, not type {type(other)}."
            )
        new_midi_num = self.midi_num + other
        if not LOWEST_PIANO_MIDI_NUM <= new_midi_num <= HIGHEST_PIANO_MIDI_NUM:
            raise ValueError(
                f"Sum is out of MIDI range: {new_midi_num} not in [0, 127]."
            )
        return Note.from_midi_num(new_midi_num)

    def __sub__(self, other):
        if not isinstance(other, int):
            raise TypeError(
                f"Can only subtract integers from Note object, not type {type(other)}."
            )
        return self.__add__(-other)

    def __eq__(self, other):
        if not isinstance(other, Note):
            return False
        return (
            self.name == other.name
            and self.symbol == other.symbol
            and self.octave == other.octave
            and self.midi_num == other.midi_num
        )

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"


@dataclass
class PatternSpec:
    index: int
    duration: float
    transpose: int = 0
    velocity: int = 80


class Chord:
    def __init__(self, notes):
        self.notes = notes

    # TODO Maybe make ArrangedNote class to replace (note, dur, vel) tuples.
    def arrange(self, pattern: List[PatternSpec]):
        arrangement = []
        for note_spec in pattern:
            note = self.notes[note_spec.index] + note_spec.transpose * NOTES_PER_OCTAVE
            duration = note_spec.duration
            velocity = note_spec.velocity
            arrangement.append((note, duration, velocity))
        return arrangement

    def __repr__(self):
        return repr(self.notes)


if __name__ == "__main__":
    assert _get_octave(21) == 0
    assert _get_octave(23) == 0
    assert _get_octave(24) == 1
    assert _get_octave(69) == 4
    assert _get_octave(108) == 8

    assert _to_note_name(21) == "A0"
    assert _to_note_name(69) == "A4"
    assert _to_note_name(70) == "A#4"
    assert _to_note_name(108) == "C8"

    assert _to_midi_num("A", 0) == 21
    assert _to_midi_num("A", 4) == 69
    assert _to_midi_num("A#", 4) == 70
    assert _to_midi_num("Bb", 4) == 70
    assert _to_midi_num("C", 8) == 108

    assert Symbol("G").index == 7
    assert Symbol("C") + 3 == Symbol("D#")
    assert Symbol("A") + 5 == Symbol("D")
    assert Symbol("D#") != Symbol("Eb")

    assert Note.from_midi_num(69) == Note("A4")
    assert Note("A4") + 1 == Note("A#4")
