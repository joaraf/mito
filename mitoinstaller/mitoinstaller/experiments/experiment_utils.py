import random
from typing import Dict, Optional


def get_random_variant() -> str:
    """Returns "A" or "B" with 50% probability"""
    return "A" if random.random() < 0.5 else "B"

def get_new_experiment() -> Dict[str, str]:
    # NOTE: this needs to match the mitosheet package!
    return {
        'experiment_id': 'no_experiment',
        'variant': 'A',
    }

def is_variant_a() -> bool:
    from mitoinstaller.user_install import get_current_experiment
    current_experiment = get_current_experiment()
    return current_experiment is None or current_experiment['variant'] == 'A'

def is_variant_b() -> bool:
    return not is_variant_a()