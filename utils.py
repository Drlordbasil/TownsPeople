import random

def generate_random_name():
    names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Isabella", "Jack",
             "Kate", "Liam", "Mia", "Nate", "Olivia", "Peter", "Quinn", "Ryan", "Sophia", "Tom"]
    return random.choice(names)


def generate_random_talent():
    talents = ["carpentry", "masonry", "electrical", "plumbing", "interior design"]
    return random.choice(talents)


def generate_random_trait():
    traits = ["helpful", "creative", "logical", "optimistic", "confident", "friendly", "patient", "resourceful", "determined", "curious"]
    return random.choice(traits)