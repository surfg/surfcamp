"""Merge 7 duplicate SurfCamp pairs on prod.

Strategy: pick the camp with the richest content as the "keeper",
move related objects from the loser to the keeper, then delete loser.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from camps.models import SurfCamp, CampImage, Instructor, Activity, Review

# (keep_id, drop_id) pairs decided after inspection
MERGES = [
    (330, 296),  # Peniche Surf Lodge
    (285, 317),  # Baleal Surf Camp — keep 285 (12 imgs), move 317's 4 instructors
    (354, 293),  # Peniche Surf Camp
    (340, 304),  # Surf Camp Lombok
    (357, 335),  # Kinetika
    (321, 289),  # Laneez Ericeira — keep 321 (28 imgs)
    (328, 294),  # Pure Surf Camp Peniche
]


@transaction.atomic
def merge():
    for keep_id, drop_id in MERGES:
        try:
            keep = SurfCamp.objects.get(pk=keep_id)
            drop = SurfCamp.objects.get(pk=drop_id)
        except SurfCamp.DoesNotExist:
            print(f'skip {keep_id}/{drop_id}: not found')
            continue

        moved_imgs = CampImage.objects.filter(camp=drop).update(camp=keep)
        moved_instr = Instructor.objects.filter(camp=drop).update(camp=keep)
        moved_act = Activity.objects.filter(camp=drop).update(camp=keep)
        moved_rev = Review.objects.filter(camp=drop).update(camp=keep)

        print(f'{keep.name} ({keep_id}<-{drop_id}): '
              f'+{moved_imgs} imgs, +{moved_instr} instr, +{moved_act} act, +{moved_rev} rev')
        drop.delete()
        print(f'  deleted SurfCamp {drop_id}')


if __name__ == '__main__':
    merge()
