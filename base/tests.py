from django.core.exceptions import ValidationError
from django.db import transaction
from unidecode import unidecode
from django.utils.text import slugify
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

# Create your tests here.
from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Cinema, Hall, Seats
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema.settings')

from django.test import TestCase
from .models import Cinema

class CinemaModelTests(TestCase):
    def test_cinema_unique_together(self):
        # Arrange
        name = 'Кінотеатр 1'
        address = 'вул. Степана Бандери, 20'

        # Act
        Cinema.objects.create(name=name, address=address)

        # Assert - спробуємо створити об'єкт з тими самим name та address
        with self.assertRaises(IntegrityError) as context:
            Cinema.objects.create(name=name, address=address)
        # self.assertIn('UNIQUE constraint', str(context.exception))

    def test_cinema_unique_together_case_insensitive(self):
        # Arrange
        name = 'Кінотеатр 1'
        address = 'вул. Степана Бандери, 20'
        name2 = 'кінотеатр 1'  # різний регістр

        # Act
        cinema=Cinema.create(name=name, address=address)
        cinema.save()

        # Assert - перевіримо, що name та address нечутливі до регістру
        with self.assertRaises(IntegrityError) as context:
            Cinema.create(name=name2, address=address)
        self.assertIn('UNIQUE constraint', str(context.exception))

    def test_cinema_unique_together_address_only(self):
        # Arrange
        name = 'Кінотеатр 1'
        address = 'вул. Степана Бандери, 20'
        address2 = 'вул. Степана Бандери, 30'  # різна адреса

        # Act
        Cinema.create(name=name, address=address).save()
        # Assert - перевіримо, що обмеження unique_together працює і для окремого поля
        with self.assertRaises(IntegrityError) as context:
            Cinema.create(name=name, address=address2)
        self.assertIn('UNIQUE constraint', str(context.exception))

    def test_empty_adress(self):
        with self.assertRaises(ValueError):
            Cinema.create(name='Кінотеатр 1', address='')


#
class CinemaModelTestCase(TestCase):
    def setUp(self):
        self.cinema = Cinema.objects.create(
            name='Кінопалац',
            address='вул. Богдана Хмельницького, 24'
        )

    def test_cinema_has_name(self):
        self.assertEqual(self.cinema.name, 'Кінопалац')

    def test_cinema_has_address(self):
        self.assertEqual(self.cinema.address, 'вул. Богдана Хмельницького, 24')

    def test_cinema_str_method(self):
        self.assertEqual(str(self.cinema), 'Кінопалац адреса: вул. Богдана Хмельницького, 24')

    def test_cinema_verbose_name_plural(self):
        self.assertEqual(str(Cinema._meta.verbose_name_plural), 'Кінотеатр')

    def test_cinema_verbose_name(self):
        self.assertEqual(str(Cinema._meta.verbose_name), 'Кінотеатри')


class HallModelTestCase(TestCase):

    def setUp(self):
        self.cinema = Cinema.objects.create(
            name='Кінопалац',
            address='вул. Богдана Хмельницького, 24'
        )

    def test_hall_address_name_is_required(self):

        with self.assertRaises(ValueError):
            Hall.create(name='', cinema=self.cinema)

        with self.assertRaises(ValueError):
            Hall.create(name=None, cinema=self.cinema)

        with self.assertRaises(TypeError):
            Hall.create(cinema=self.cinema)



    def test_create_hall(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.create(name='Зал 1', cinema=self.cinema)

        # Перевірка того, що екземпляр моделі був створений коректно
        self.assertIsInstance(hall, Hall)
        self.assertEqual(hall.name, 'Зал 1')
        self.assertEqual(hall.cinema, self.cinema)

    def test_capacity(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.create(name = 'Зал 1', cinema = self.cinema)
        hall.save()

        # Створення трьох екземплярів моделі Seat з допустимими даними та прив'язка до залу
        seat1 = Seats.objects.create(number=1, raw=1, hall = hall)
        seat2 = Seats.objects.create(number=2, raw=1, hall = hall)
        seat3 = Seats.objects.create(number=3, raw=1, hall = hall)

        # Перевірка того, що метод capacity повертає очікувану ємність залу
        self.assertEqual(hall.capacity(), 3)

    def test_capacity_2(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name = 'Зал 1', cinema = self.cinema)


        # Створення трьох екземплярів моделі Seat з допустимими даними та прив'язка до залу
        seat1 = Seats.objects.create(number=1, raw=1,  hall = hall)
        seat2 = Seats.objects.create(number=2, raw=1,  hall = hall)
        seat3 = Seats.objects.create(number=3, raw=1,  hall = hall)

        # Створення двох екземплярів моделі Seat з допустимими даними та прив'язка до залу
        seat1 = Seats.objects.create(number=1, raw=2,  hall = hall)
        seat2 = Seats.objects.create(number=2, raw=2,  hall = hall)
        # Перевірка того, що метод capacity повертає очікувану ємність залу
        self.assertEqual(hall.capacity(), 5)


    def test_delete_hall(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name='Зал 1', cinema=self.cinema)

        # Створення екземпляру моделі Seat з допустимими даними та прив'язка до ряду
        seat1 = Seats.objects.create(number=2, raw=1, hall = hall )

        # Видалення екземпляру моделі з бази даних
        hall.delete()

        # Перевірка того, що екземпляр моделі був видалений з бази даних
        with self.assertRaises(Hall.DoesNotExist):
            Hall.objects.get(id=hall.id)


class HallModelUniqueTestCase(TestCase):

    def setUp(self):
        self.cinema1 = Cinema.objects.create(name='Кінотеатр 1', address='вул. Богдана Хмельницького, 24')
        self.cinema2 = Cinema.objects.create(name='Кінотеатр 2', address='вул. Богдана Хмельницького, 34')
        self.hall1 = Hall.objects.create(name='Зал 1', cinema=self.cinema1)

    def test_unique_together(self):
        # Перевіряємо, що не можна створити зал з таким самим ім'ям та для того ж кінотеатру
        with transaction.atomic():
            with self.assertRaises(IntegrityError) as context:
                Hall.objects.create(name='Зал 1', cinema=self.cinema1)
        self.assertTrue('unique constraint' in str(context.exception))

            # Перевіряємо, що можна створити зал з таким самим ім'ям, але для іншого кінотеатру
        with transaction.atomic():
            hall2 = Hall.objects.create(name='Зал 1', cinema=self.cinema2)
            self.assertIsNotNone(hall2.id)




class SeatsModelTest(TestCase):

    def setUp(self):
        self.cinema = Cinema.objects.create(name='Кінотеатр',address='вул. Богдана Хмельницького, 24')
        self.hall = Hall.objects.create(name='Червоний', cinema=self.cinema)
        self.seat = Seats.objects.create(number=1, raw=1, hall=self.hall)

    def test_str(self):
        # Перевіряємо, що метод __str__ повертає очікуваний рядок
        expected_str = ' '.join((str(self.cinema), str(self.hall), _("Ряд: ") + f"{self.seat.raw}", _("Місце: ") + f"{self.seat.number}"))
        self.assertEqual(str(self.seat), expected_str)

class CinemaModelRequaedTestCase(TestCase):
    def setUp(self):
        self.cinema = Cinema.objects.create(
            name='Кінотеатр "Україна"',
            address='вул. Хрещатик, 22'
        )

    def test_cinema_name_field_is_required(self):

        with self.assertRaises(ValueError):
            cinema = Cinema.create(name=None, address='вул. Хрещатик, 22')

    def test_cinema_address_field_is_required(self):

        with self.assertRaises(IntegrityError):
            cinema = Cinema.objects.create(name='Кінотеатр "Україна"', address=None)

    def test_cinema_fields_are_not_blank(self):

        with self.assertRaises(ValidationError):
            cinema = Cinema(name='', address='')
            cinema.full_clean()

    def test_cinema_object_creation(self):
        self.assertEqual(Cinema.objects.count(), 1)
        self.assertEqual(self.cinema.name, 'Кінотеатр "Україна"')
        self.assertEqual(self.cinema.address, 'вул. Хрещатик, 22')

    def test_slug_field_is_created_on_save(self):
        cinema = Cinema.objects.create(name="Кінотеатр Імакс", address="вул. Шевченка 1")
        self.assertEqual(cinema.slug, slugify(unidecode(cinema.name)))

class HallFillTestCase(TestCase):
    def setUp(self):
        cinema = Cinema.objects.create(name='Кінотеатр', address="вул. Шевченка 1")
        self.hall = Hall.objects.create(name='Зал 1', cinema=cinema)

    def test_fill_hall_with_seats(self):

        self.hall.fill_hall(5, 6, 7)

        self.assertEqual(self.hall.get_num_of_row(), 3)
        self.assertEqual(self.hall.get_num_of_sets_in_row(1), 5)
        self.assertEqual(self.hall.get_num_of_sets_in_row(3), 7)

    def test_fill_hall_without_seats(self):
        self.hall.fill_hall()
        self.assertEqual(self.hall.seats_set.count(), 0)