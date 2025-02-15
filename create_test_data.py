import random

import lorem

from apps.gallery.models import Product as P, ProductCategory as C


def create_test_categories():
    print("...creating categories:")

    cBowl = C(name="Bowl")
    cBowl.save()
    print(f"--category {cBowl.name} created")

    cPlatter = C(name="Platter")
    cPlatter.save()
    print(f"--category {cPlatter.name} created")

    cPot = C(name="Pot")
    cPot.save()
    print(f"--category {cPot.name} created")

    print(f"...done ({C.objects.count()} categories created)")
    return


def create_test_products():

    print()
    print("...creating products:")

    for i in range(21):
      o = P(
          name=lorem.get_word(count=(1, 5), sep=' ').capitalize(),
          description=lorem.get_sentence(count=4, comma=(0,2), word_range=(8, 15), sep=' '),
      )
      o.save()
      # o.category.set([C.objects.get(name=product[1]).id])
      categories = C.objects.all()
      o.category.set([random.choice(categories).id])

      print(f"--{o.category.first().name} named '{o.name}' created")

    print(f"...done ({P.objects.count()} products created)")
    return

print("Checking database for data...")
if (num_categories := C.objects.count()) == 0: create_test_categories()
if (num_products := P.objects.count()) == 0: create_test_products()

