"""
A module for optimization algorithms.

"""

from note_seq.protobuf import music_pb2
from . import util
from . import constants

#think about input note_sequence
def calculate_score_of_new_note(key, chord_progression, previous_notes, new_note):

    score = 0
    generated_note = new_note

    # valid note for key
    if generated_note in notes_per_key[key]:
        score += constants.NOTE_IN_KEY_REWARD
    else
        score -= constants.NOTE_IN_KEY_REWARD

    # note in chord
    if generated_note in [item for sublist in chord_progression for item in sublist]:
        score += constants.NOTE_IN_CHORDS_REWARD

    ### Consonant ###
    # Perfect unison
    if generated_note in util.all_octaves(previous_notes[-1]):
        score += constants.CONSONANT_INTERVAL_REWARD
    # perfect fourth
    if generated_note in util.all_octaves(previous_notes[-1]+5):
        score += constants.CONSONANT_INTERVAL_REWARD
    # perfect fifth
    if generated_note in util.all_octaves(previous_notes[-1]+7):
        score += constants.SUPER_CONSONANT_INTERVAL_REWARD
    ### Dissonant ###
    # Minor second
    if generated_note in util.all_octaves(previous_notes[-1]+1):
        score += constants.DISSONANT_INTERVAL_REWARD

    # centricity
    score += previous_notes.count(generated_note)*constants.CENTRICITY_FACTOR
    
    return score

def value_fn(key, chord_progression, note_sequence: music_pb2.NoteSequence) -> float:
    """
    A scalar-valued function that assigns a score to every note sequence.

    """
    ...

    # for all sub sequences starting from first 2 notes, call calculate_score_of_generated_note and sum up scores
    # can't find class for NoteSequence from Magenta (IDE?)
    
    score = 0
    
    pitches = util.extract_pitches(note_sequence)
    
    for end, pitch in enumerate(pitches[1:], 1):
    
        score += calculate_score_of_new_note(key, chord_progression, pitches[:end], pitch)
    
    return score



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
    # hold one object at a time, assess next note, add it to object 
    # randomly pick a key
    key = utils.get_random_key()
    
    # get a chord progression
    chord_progression = utils.build_chord_progression(key)
    
    desired_length = 10
    best_note_seq = music_pb2.NoteSequence()
    
    # randomly pick first note
    best_note_seq.notes.add(pitch=utils.get_random_note_from_key(key), start_time=0.0, end_time=1.0, velocity=80)
    
    for i in range(1, desired_length):
        
        # dict of score : list of notes
        new_note_scores = {}
        
        for new_note in constants.NOTES_FOR_KEY[key]:
            
            # for each note, calculate its score. 
            score = value_fn(key, chord_progression, util.extract_pitches(best_note_seq), new_note)
            
            new_note_scores.setdefault(score,[]).append(new_note)
            
        
        # If there is a tie for highest score, randomly pick from the tied notes
        
        selected_note = random.choice(new_note_scores[max(new_note_scores.keys())])
        
        best_note_seq.notes.add(pitch=selected_note, start_time=i*1.0, end_time=i*1.0+1.0, velocity=80)
            
    return best_note_seq
        
        


def get_candidates(note_seq: music_pb2.NoteSequence) -> list[music_pb2.NoteSequence]:
    """
    Create a list of candidate sequences given a start sequence. Every sequence is
    exactly one note longer than the original sequence. This note should be in the same
    key as the original sequence.

    """
    ...