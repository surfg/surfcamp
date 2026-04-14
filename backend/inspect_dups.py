import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import SurfCamp
from django.db.models import Count

dups = SurfCamp.objects.values('name', 'region').annotate(c=Count('id')).filter(c__gt=1)
for d in dups:
    camps = SurfCamp.objects.filter(name=d['name'], region_id=d['region']).order_by('id')
    print(f"\n=== {d['name']} (region {d['region']}) ===")
    for c in camps:
        print(f"  id={c.id} slug={c.slug} imgs={c.images.count()} instr={c.instructors.count()} bk={c.bookings.count()} act={c.is_active} feat={c.is_featured}")
