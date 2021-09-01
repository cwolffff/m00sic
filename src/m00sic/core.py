"""Core classes and methods.

Nomenclature:
- A PitchClass is a combination of a letter and, optionally, an accidental, e.g. 'A#'.
- A Note is a note symbol followed by an octave, e.g. 'A#4'.
- A Chord is a list of Notes.
- The rank of a note is an integer that indicates its position within its octave. It's
always between 0 and 11.

"""


from __future__ import annotations

import abc
import dataclasses
import re
from enum import Enum, auto
from typing import List

from note_seq.protobuf import music_pb2


# Durations.
W = WHOLE = 1
H = HALF = 1 / 2
Q = QUARTER = 1 / 4
E = EIGHTH = 1 / 8
S = SIXTEENTH = 1 / 16


PITCH_CLASSES = [
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
VALID_PITCH_CLASSES = {
    pitch_class
    for pitch_class_tuple in PITCH_CLASSES
    for pitch_class in pitch_class_tuple
}
_PITCH_CLASS_TO_RANK = {
    pitch_class: rank
    for rank, pitch_class_tuple in enumerate(PITCH_CLASSES)
    for pitch_class in pitch_class_tuple
}


_C0_MIDI_NUM = 12
LOWEST_PIANO_MIDI_NUM = 21  # A0
HIGHEST_PIANO_MIDI_NUM = 108  # C8


LOWEST_PIANO_OCTAVE = 0
HIGHEST_PIANO_OCTAVE = 8
NOTES_PER_OCTAVE = 12


def _get_octave(midi_num: int):
    return (midi_num - _C0_MIDI_NUM) // NOTES_PER_OCTAVE


def _get_rank(midi_num: int):
    return (midi_num - _C0_MIDI_NUM) % NOTES_PER_OCTAVE


def _to_note_name(midi_num: int):
    assert midi_num >= _C0_MIDI_NUM
    octave = _get_octave(midi_num)
    rank = _get_rank(midi_num)
    symbol_names = PITCH_CLASSES[rank]
    return f"{symbol_names[0]}{octave}"


def _to_midi_num(symbol_name: str, octave: int):
    rank = _PITCH_CLASS_TO_RANK[symbol_name]
    return _C0_MIDI_NUM + NOTES_PER_OCTAVE * octave + rank


def _get_trailing_number(s: str):
    m = re.search(r"\d+$", s)
    return m.group() if m else None


@dataclasses.dataclass
class PitchClass:
    """A musical pitch class, e.g. 'G#' or 'B'."""

    name: str
    index: int = dataclasses.field(init=False)

    def __post_init__(self):
        assert self.name in VALID_PITCH_CLASSES
        self.index = _PITCH_CLASS_TO_RANK[self.name]

    def __add__(self, other: object) -> PitchClass:
        if not isinstance(other, int):
            raise TypeError(
                f"Can only add integers to PitchClass object, not type {type(other)}."
            )
        new_index = (self.index + other) % NOTES_PER_OCTAVE
        new_name = PITCH_CLASSES[new_index][0]
        return PitchClass(new_name)

    def __sub__(self, other: object) -> PitchClass:
        if not isinstance(other, int):
            raise TypeError(
                f"Can only subtract integers from PitchClass object, "
                f"not type {type(other)}."
            )
        return self.__add__(-other)


class Note:
    def __init__(self, name: str):
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
        pitch_class = name[:-octave_nchar]
        assert pitch_class in VALID_PITCH_CLASSES

        self.name = name
        self.pitch_class = PitchClass(pitch_class)
        self.octave = octave
        self.midi_num = _to_midi_num(pitch_class, octave)

    @classmethod
    def from_midi_num(cls, midi_num: int) -> Note:
        assert LOWEST_PIANO_MIDI_NUM <= midi_num <= HIGHEST_PIANO_MIDI_NUM
        name = _to_note_name(midi_num)
        return cls(name)

    def __add__(self, other: object) -> Note:
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

    def __sub__(self, other: object) -> Note:
        if not isinstance(other, int):
            raise TypeError(
                f"Can only subtract integers from Note object, not type {type(other)}."
            )
        return self.__add__(-other)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return False
        return (
            self.name == other.name
            and self.pitch_class == other.pitch_class
            and self.octave == other.octave
            and self.midi_num == other.midi_num
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"


@dataclasses.dataclass
class Chord:

    notes: List[Note]

    # TODO Add __add__ and __sub__


# TODO Fix pitch classes in __repr__. The same letter shouldn't appear more than once.
class Key(abc.ABC):
    def __init__(self, name):
        assert name in VALID_PITCH_CLASSES
        self.name = name

    @property
    @abc.abstractmethod
    def intervals(self):
        ...

    @property
    def pitch_classes(self):
        return [PitchClass(self.name) + i for i in self.intervals]

    def _get_interval(self, degree):
        offset = 0
        if degree >= 0:
            while degree >= len(self.intervals):
                offset += NOTES_PER_OCTAVE
                degree -= len(self.intervals)
        else:
            while degree < 0:
                offset -= NOTES_PER_OCTAVE
                degree += len(self.intervals)
        return self.intervals[degree] + offset

    def get_note(self, degree, octave=4) -> Note:
        scale_starting_note = Note(f"{self.name}{octave}")
        return scale_starting_note + self._get_interval(degree)

    def get_chord(self, positions, degree=0, octave=4, inversion=0) -> Chord:
        notes = [
            self.get_note(degree + position, octave=octave) for position in positions
        ]
        for _ in range(abs(inversion)):
            if inversion < 0:
                notes = notes[:-1] + [notes[-1] - NOTES_PER_OCTAVE]
            else:
                notes = notes[1:] + [notes[0] + NOTES_PER_OCTAVE]
        return Chord(notes)

    def get_triad(self, degree, octave=4, inversion=0) -> Chord:
        return self.get_chord(
            positions=[0, 2, 4], degree=degree, octave=octave, inversion=inversion
        )

    def get_seventh(self, degree, octave=4, inversion=0) -> Chord:
        return self.get_chord(
            positions=[0, 2, 4, 6], degree=degree, octave=octave, inversion=inversion
        )

    def get_ninth(self, degree, octave=4, inversion=0) -> Chord:
        return self.get_chord(
            positions=[0, 2, 4, 6, 8], degree=degree, octave=octave, inversion=inversion
        )

    def get_eleventh(self, degree, octave=4, inversion=0) -> Chord:
        return self.get_chord(
            positions=[0, 2, 4, 6, 8, 10],
            degree=degree,
            octave=octave,
            inversion=inversion,
        )

    def get_thirteenth(self, degree, octave=4, inversion=0) -> Chord:
        return self.get_chord(
            positions=[0, 2, 4, 6, 8, 10, 12],
            degree=degree,
            octave=octave,
            inversion=inversion,
        )

    def __repr__(self):
        pitch_class_str = ", ".join(
            [pitch_class.name for pitch_class in self.pitch_classes]
        )
        return f"{self.__class__.__name__}({pitch_class_str})"


class MajorKey(Key):

    _intervals = [0, 2, 4, 5, 7, 9, 11]

    @property
    def intervals(self):
        return self._intervals


class MinorKey(Key):

    _intervals = [0, 2, 3, 5, 7, 8, 10]

    @property
    def intervals(self):
        return self._intervals


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

    assert PitchClass("G").index == 7
    assert PitchClass("C") + 3 == PitchClass("D#")
    assert PitchClass("A") + 5 == PitchClass("D")
    assert PitchClass("D#") != PitchClass("Eb")

    assert Note.from_midi_num(69) == Note("A4")
    assert Note("A4") + 1 == Note("A#4")

    assert str(MajorScale("C")) == "MajorScale(C, D, E, F, G, A, B)"
