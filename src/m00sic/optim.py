"""
A module for optimization algorithms.

"""

from note_seq.protobuf import music_pb2


def value_fn(note_sequence: music_pb2.NoteSequence) -> float:
    """
    A scalar-valued function that assigns a score to every note sequence.

    """
    ...


def local_search(value_fn: function) -> music_pb2.NoteSequence:
    """
    An optimization procedure that tries to find a note sequence with a high value,
    by greedily adding notes that result in the largest value.

    There are serveral possible ways of implementing this. One simple way would be to
    define the candidate set of next sequences as all sequences with one additional
    note at the end. For simplicity, all note lengths could be fixed, and all sequences
    could be monophonic. Then, we simply start with an empty sequence and greedily add
    notes until we reach some desired sequence length.
    
    """
    ...