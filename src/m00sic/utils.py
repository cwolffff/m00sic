import dataclasses
import math
from typing import List

from note_seq.protobuf import music_pb2

from m00sic.core import Chord
from m00sic.core import Note
from m00sic.core import NOTES_PER_OCTAVE


# A token to indicate that a note should be starting after the previous note.
# Generated using uuid.uuid1().
AFTER = "ec79a478-fbf2-11eb-9430-acbc32aea1ef"


@dataclasses.dataclass
class PatternSpec:
    index: int
    start_time: float
    duration: float
    start_margin: float = 0.0
    end_margin: float = 0.0
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
        t = start_time + ps.duration
        t_max = max(t, t_max)
    seq.total_time = t_max
    return seq


def arrange_melody():
    # TODO
    ...


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