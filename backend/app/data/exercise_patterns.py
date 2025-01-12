"""
Exercise patterns database with muscle activation patterns
"""

EXERCISE_PATTERNS = {
    "squat": {
        "variations": ["back squat", "front squat", "bodyweight squat"],
        "movement_pattern": "squat",
        "muscle_activations": [
            {"muscle_name": "quadriceps", "activation_level": "PRIMARY", "estimated_volume": 1.0},
            {"muscle_name": "gluteus_maximus", "activation_level": "PRIMARY", "estimated_volume": 0.9},
            {"muscle_name": "hamstrings", "activation_level": "SECONDARY", "estimated_volume": 0.6},
            {"muscle_name": "core", "activation_level": "TERTIARY", "estimated_volume": 0.3}
        ],
        "equipment_needed": ["barbell", "rack"],
    },
    "deadlift": {
        "variations": ["conventional deadlift", "romanian deadlift", "sumo deadlift"],
        "movement_pattern": "hinge",
        "muscle_activations": [
            {"muscle_name": "hamstrings", "activation_level": "PRIMARY", "estimated_volume": 1.0},
            {"muscle_name": "gluteus_maximus", "activation_level": "PRIMARY", "estimated_volume": 0.9},
            {"muscle_name": "lower_back", "activation_level": "PRIMARY", "estimated_volume": 0.8},
            {"muscle_name": "trapezius", "activation_level": "SECONDARY", "estimated_volume": 0.6},
            {"muscle_name": "forearms", "activation_level": "SECONDARY", "estimated_volume": 0.5}
        ],
        "equipment_needed": ["barbell"],
    },
    "bench_press": {
        "variations": ["flat bench press", "incline bench press", "decline bench press"],
        "movement_pattern": "push",
        "muscle_activations": [
            {"muscle_name": "pectoralis_major", "activation_level": "PRIMARY", "estimated_volume": 1.0},
            {"muscle_name": "anterior_deltoid", "activation_level": "PRIMARY", "estimated_volume": 0.8},
            {"muscle_name": "triceps", "activation_level": "SECONDARY", "estimated_volume": 0.7},
            {"muscle_name": "core", "activation_level": "TERTIARY", "estimated_volume": 0.3}
        ],
        "equipment_needed": ["barbell", "bench"],
    },
    "row": {
        "variations": ["barbell row", "dumbbell row", "pendlay row"],
        "movement_pattern": "pull",
        "muscle_activations": [
            {"muscle_name": "latissimus_dorsi", "activation_level": "PRIMARY", "estimated_volume": 1.0},
            {"muscle_name": "rhomboids", "activation_level": "PRIMARY", "estimated_volume": 0.8},
            {"muscle_name": "biceps", "activation_level": "SECONDARY", "estimated_volume": 0.7},
            {"muscle_name": "rear_deltoid", "activation_level": "SECONDARY", "estimated_volume": 0.6},
            {"muscle_name": "core", "activation_level": "TERTIARY", "estimated_volume": 0.4}
        ],
        "equipment_needed": ["barbell"],
    },
    "overhead_press": {
        "variations": ["standing press", "seated press", "push press"],
        "movement_pattern": "push",
        "muscle_activations": [
            {"muscle_name": "anterior_deltoid", "activation_level": "PRIMARY", "estimated_volume": 1.0},
            {"muscle_name": "triceps", "activation_level": "PRIMARY", "estimated_volume": 0.8},
            {"muscle_name": "upper_pectoralis", "activation_level": "SECONDARY", "estimated_volume": 0.6},
            {"muscle_name": "core", "activation_level": "TERTIARY", "estimated_volume": 0.4}
        ],
        "equipment_needed": ["barbell"],
    },
    "pull_up": {
        "variations": ["chin up", "neutral grip pull up", "wide grip pull up"],
        "movement_pattern": "pull",
        "muscle_activations": [
            {"muscle_name": "latissimus_dorsi", "activation_level": "PRIMARY", "estimated_volume": 1.0},
            {"muscle_name": "biceps", "activation_level": "PRIMARY", "estimated_volume": 0.8},
            {"muscle_name": "rhomboids", "activation_level": "SECONDARY", "estimated_volume": 0.7},
            {"muscle_name": "core", "activation_level": "TERTIARY", "estimated_volume": 0.3}
        ],
        "equipment_needed": ["pull_up_bar"],
    }
}
