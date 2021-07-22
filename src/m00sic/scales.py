import abc

from .core import Chord, Note, Symbol
from .core import VALID_SYMBOL_NAMES, NOTES_PER_OCTAVE


# TODO Fix symbol names in __repr__. The same letter shouldn't appear more than once.
class Scale(abc.ABC):
    def __init__(self, name):
        assert name in VALID_SYMBOL_NAMES
        self.name = name

    @property
    @abc.abstractmethod
    def intervals(self):
        ...

    @property
    def symbols(self):
        return [Symbol(self.name) + i for i in self.intervals]

    def _get_interval(self, degree):
        offset = 0
        while degree > len(self.intervals):
            offset += NOTES_PER_OCTAVE
            degree -= len(self.intervals)
        return self.intervals[degree - 1] + offset

    # TODO Maybe change to get_chord and add "type" arg that can e.g. be "triad".
    # TODO Use list of semitones (e.g. [0, 4, 7]) to get notes for chord.
    def get_triad(self, degree, inversion=0, octave=4) -> Chord:
        assert degree >= 1
        assert inversion in [0, 1, 2]
        scale_starting_note = Note(f"{self.name}{octave}")
        triad = [
            scale_starting_note + self._get_interval(degree + offset)
            for offset in (0, 2, 4)
        ]
        if inversion == 1:
            triad = [triad[2] - NOTES_PER_OCTAVE, triad[0], triad[1]]
        elif inversion == 2:
            triad = [triad[2] - NOTES_PER_OCTAVE, triad[1] - NOTES_PER_OCTAVE, triad[0]]
        return Chord(triad)

    def __repr__(self):
        symbols_str = ", ".join([symbol.name for symbol in self.symbols])
        return f"{self.__class__.__name__}({symbols_str})"


class MajorScale(Scale):

    _intervals = [0, 2, 4, 5, 7, 9, 11]

    @property
    def intervals(self):
        return self._intervals


class MinorScale(Scale):

    _intervals = [0, 2, 3, 5, 7, 8, 10]

    @property
    def intervals(self):
        return self._intervals


if __name__ == "__main__":
    assert str(MajorScale("C")) == "MajorScale(C, D, E, F, G, A, B)"
    assert MajorScale("A").get_triad(4) == [Note("D5"), Note("F#5"), Note("A5")]