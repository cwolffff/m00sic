"""
Runner

"""



from . import optim

if __name__ == "__main__":
    
    print(optim.local_search(optim.calculate_score_of_new_note))