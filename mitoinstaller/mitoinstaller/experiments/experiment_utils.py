import random
from typing import Dict, Optional


def get_random_variant() -> str:
    """Returns "A" or "B" with 50% probability"""
    return "A" if random.random() < 0.5 else "B"

def get_new_experiment() -> Optional[Dict[str, str]]:
    # NOTE: this needs to match the mitosheet package!
    return {
        'experiment_id': 'title_name',
        'variant': get_random_variant(),
    }

def is_variant_a() -> bool:
    from mitoinstaller.user_install import get_current_experiment
    current_experiment = get_current_experiment()
    print("Current", current_experiment)
    return current_experiment is None or ['variant'] == 'A'

def is_variant_b() -> bool:
    return not is_variant_a()