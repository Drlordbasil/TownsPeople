import random

def generate_random_name():
    names = [
        "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Isabella", "Jack",
        "Kate", "Liam", "Mia", "Nate", "Olivia", "Peter", "Quinn", "Ryan", "Sophia", "Tom",
        "Uma", "Victor", "Wendy", "Xavier", "Yara", "Zoe", "Adam", "Bella", "Chloe", "Daniel",
        "Ella", "Finn", "Gina", "Harry", "Ivy", "James", "Kira", "Leo", "Mila", "Noah", "Orla",
        "Paul", "Quinn", "Rose", "Sam", "Tessa", "Uriah", "Violet", "Will", "Xena", "Yves", "Zara"
    ]
    return random.choice(names)

def generate_random_talent():
    talents = [
        "carpentry", "masonry", "electrical", "plumbing", "interior design", "landscaping",
        "programming", "engineering", "arts and crafts", "cooking", "music", "writing",
        "teaching", "healthcare", "public speaking", "marketing", "finance", "law",
        "environmental science", "agriculture"
    ]
    return random.choice(talents)

def generate_random_trait():
    traits = [
        "helpful", "creative", "logical", "optimistic", "confident", "friendly", "patient",
        "resourceful", "determined", "curious", "adaptable", "empathetic", "organized",
        "cooperative", "perceptive", "resilient", "passionate", "intuitive", "charismatic",
        "humble", "adventurous", "analytical", "persuasive", "dependable", "courageous"
    ]
    return random.choice(traits)
