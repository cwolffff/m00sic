import dataclasses
import math
from typing import List, Union

from note_seq.protobuf import music_pb2

from m00sic.core import Chord
from m00sic.core import Note
from m00sic.core import NOTES_PER_OCTAVE


# A token to indicate that a note should be starting after the previous note.
# Generated using uuid.uuid1().
AFTER = 87178770498530249949750886040005943791
PAUSE = 92888580960918501375582155840183771631


@dataclasses.dataclass
class PatternSpec:
    """A specification used to define patterns.

    Patterns are lists of PatternSpecs and indicate how a given chord should be
    arranged. For example,

    >> pattern = [
        PS(index=0, start_time=0, duration=EIGHTH),
        PS(index=1, start_time=AFTER, duration=EIGHTH),
        PS(index=2, start_time=AFTER, duration=QUARTER),
    ]

    indicates that the first note (index 0) should be played for an EIGHTH duration,
    then the second note (index 1) should be played for an EIGHTH duration, and finally
    the third note (index 2) should be played for a QUARTER duration.
    """

    index: int
    start_time: float
    duration: float
    end_margin: float = 0.0
    start_margin: float = 0.0
    transpose: int = 0
    velocity: int = 80


@dataclasses.dataclass
class NoteSpec:
    """A specification for how a specific note should be played."""

    note: Union[Note, str]
    duration: float
    end_margin: float = 0.0
    start_margin: float = 0.0
    transpose: int = 0
    velocity: int = 80

    def __post_init__(self):
        if isinstance(self.note, str):
            self.note = Note(self.note)


@dataclasses.dataclass
class ChordSpec:
    """A specification for how a specific chord should be played."""

    chord: Chord
    duration: float
    end_margin: float = 0.0
    start_margin: float = 0.0
    transpose: int = 0
    velocity: int = 80


def arrange_chord(chord: Chord, pattern: List[PatternSpec]) -> music_pb2.NoteSequence:
    """Arrange a list of notes in a given pattern."""
    seq = music_pb2.NoteSequence()
    t = 0.0
    t_max = -math.inf
    for ps in pattern:
        total_margin = ps.start_margin + ps.end_margin
        assert ps.duration > total_margin
        note = chord.notes[ps.index] + ps.transpose * NOTES_PER_OCTAVE
        start_time = t if ps.start_time == AFTER else ps.start_time
        end_time = start_time + ps.duration
        seq.notes.add(
            pitch=note.midi_num,
            start_time=start_time + ps.start_margin,
            end_time=end_time - ps.end_margin,
            velocity=ps.velocity,
        )
        t = end_time
        t_max = max(t, t_max)
    seq.total_time = t_max
    return seq


def arrange_melody(
    note_or_chord_specs: Union[NoteSpec, ChordSpec]
) -> music_pb2.NoteSequence:
    """Arrange a list of NoteSpec or ChordSpec objects into a melody."""
    seq = music_pb2.NoteSequence()
    t = 0.0
    for spec in note_or_chord_specs:
        if spec.note != PAUSE:
            total_margin = spec.start_margin + spec.end_margin
            assert spec.duration > total_margin
            note = spec.note + spec.transpose * NOTES_PER_OCTAVE
            start_time = t
            end_time = start_time + spec.duration
            seq.notes.add(
                pitch=note.midi_num,
                start_time=start_time + spec.start_margin,
                end_time=end_time - spec.end_margin,
                velocity=spec.velocity,
            )
        t += spec.duration
    seq.total_time = t
    return seq


def concat_sequences(*seqs):
    """Concatenate note sequences horizontally."""
    concat_seqs = music_pb2.NoteSequence()
    concat_seqs.total_time = sum([seq.total_time for seq in seqs])
    t = 0.0
    for seq in seqs:
        for note in seq.notes:
            start_time = t + note.start_time
            end_time = t + note.end_time
            concat_seqs.notes.add(
                pitch=note.pitch,
                start_time=start_time,
                end_time=end_time,
                velocity=note.velocity,
            )
        t += seq.total_time
    return concat_seqs


def stack_sequences(*seqs):
    """Stack note sequences on top of each other."""
    stacked_seqs = music_pb2.NoteSequence()
    stacked_seqs.total_time = max([seq.total_time for seq in seqs])
    for seq in seqs:
        for note in seq.notes:
            stacked_seqs.notes.add(
                pitch=note.pitch,
                start_time=note.start_time,
                end_time=note.end_time,
                velocity=note.velocity,
            )
    return stacked_seqs