import random

import lorem

from .models import Product as P
from .models import ProductCategory as C


def create_test_categories():
    """Create test categories for use in development."""

    print("...creating categories:")
    categories = ["Bowl", "Platter", "Mug", "Pot", "Flower Pot"]

    for category in categories:
        o = C(name=category)
        o.save()
        print(f"----category '{o.name}' created")

    print(f"...{C.objects.count()} categories created")
    print()
    return


def create_test_products():
    """Create test categories for use in development."""
    num_of_products = int(input("How many test products should be created?"))
    print("...creating products:")

    for i in range(num_of_products):
        o = P(
            name=lorem.get_word(count=(1, 5), sep=" ").capitalize(),
            description=lorem.get_sentence(
                count=4, comma=(0, 2), word_range=(8, 15), sep=" "
            ),
        )
        o.save()
        # o.category.set([C.objects.get(name=product[1]).id])
        categories = C.objects.all()
        o.category.set([random.choice(categories).id])

        print(f"----{o.category.first().name} named '{o.name}' created")

    print(f"...{P.objects.count()} products created")
    return


def create_test_data():
    """Check for data in development database, and create test data."""

    print("Checking database for data...")
    if (num_categories := C.objects.count()) == 0:
        create_test_categories()
    if (num_products := P.objects.count()) == 0:
        create_test_products()
    print()
    print("...done")
    return
