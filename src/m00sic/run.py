"""
Runner generates one sample

"""

import datetime
import note_seq
from m00sic import optim


# when include_chords=True adds in base chord structure, else only generates melody line
if __name__ == "__main__":

    generated_note_sequence = optim.local_search(
        optim.calculate_score_of_new_note, include_chords=True
    )

    note_seq.note_sequence_to_midi_file(
        generated_note_sequence, "generated_{}.midi".format(datetime.datetime.now())
    )
