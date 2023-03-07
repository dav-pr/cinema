from django.db import transaction
from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Cinema, Hall, Raw, Seats
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
        self.assertIn('UNIQUE constraint', str(context.exception))

    def test_cinema_unique_together_case_insensitive(self):
        # Arrange
        name = 'Кінотеатр 1'
        address = 'вул. Степана Бандери, 20'
        name2 = 'кінотеатр 1'  # різний регістр

        # Act
        Cinema.objects.create(name=name, address=address)

        # Assert - перевіримо, що name та address нечутливі до регістру
        with self.assertRaises(IntegrityError) as context:
            Cinema.objects.create(name=name2, address=address)
        self.assertIn('UNIQUE constraint', str(context.exception))

    def test_cinema_unique_together_address_only(self):
        # Arrange
        name = 'Кінотеатр 1'
        address = 'вул. Степана Бандери, 20'
        address2 = 'вул. Степана Бандери, 30'  # різна адреса

        # Act
        Cinema.objects.create(name=name, address=address)
        # Assert - перевіримо, що обмеження unique_together працює і для окремого поля
        with self.assertRaises(IntegrityError) as context:
            Cinema.objects.create(name=name, address=address2)
        self.assertIn('UNIQUE constraint', str(context.exception))

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

    def test_create_hall(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name='Зал 1', cinema=self.cinema)

        # Перевірка того, що екземпляр моделі був створений коректно
        self.assertIsInstance(hall, Hall)
        self.assertEqual(hall.name, 'Зал 1')
        self.assertEqual(hall.cinema, self.cinema)

    def test_capacity(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name = 'Зал 1', cinema = self.cinema)

        # Створення екземпляру моделі Raw з допустимими даними та прив'язка до залу
        raw = Raw.objects.create(number = 1, hall = hall)

        # Створення трьох екземплярів моделі Seat з допустимими даними та прив'язка до ряду
        seat1 = Seats.objects.create(number=1, raw=raw)
        seat2 = Seats.objects.create(number=2, raw=raw)
        seat3 = Seats.objects.create(number=3, raw=raw)

        # Перевірка того, що метод capacity повертає очікувану ємність залу
        self.assertEqual(hall.capacity(), 3)
        raw.delete()

    def test_capacity_2(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name = 'Зал 1', cinema = self.cinema)

        # Створення екземпляру моделі Raw з допустимими даними та прив'язка до залу
        raw0 = Raw.objects.create(number = 1, hall = hall)
        raw1 = Raw.objects.create(number = 2, hall = hall)


        # Створення трьох екземплярів моделі Seat з допустимими даними та прив'язка до ряду
        seat1 = Seats.objects.create(number=1, raw=raw0)
        seat2 = Seats.objects.create(number=2, raw=raw0)
        seat3 = Seats.objects.create(number=3, raw=raw0)

        # Створення двох екземплярів моделі Seat з допустимими даними та прив'язка до ряду
        seat1 = Seats.objects.create(number=1, raw=raw1)
        seat2 = Seats.objects.create(number=2, raw=raw1)
        # Перевірка того, що метод capacity повертає очікувану ємність залу
        self.assertEqual(hall.capacity(), 5)

    def test_capacity_3(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name = 'Зал 1', cinema = self.cinema)
        # Створення екземпляру моделі Raw з допустимими даними та прив'язка до залу
        raw0 = Raw.objects.create(number = 1, hall = hall)
        raw0.add_sets(10, Seats)
        raw1 = Raw.objects.create(number = 2, hall = hall)
        raw1.add_sets(3, Seats)

        # Перевірка того, що метод capacity повертає очікувану ємність залу
        self.assertEqual(hall.capacity(), 13)

    def test_delete_hall(self):
        # Створення екземпляру моделі Hall з допустимими даними
        hall = Hall.objects.create(name='Зал 1', cinema=self.cinema)

        # Створення екземпляру моделі Raw з допустимими даними та прив'язка до залу
        raw = Raw.objects.create(number = 1, hall = hall)

        # Створення екземпляру моделі Seat з допустимими даними та прив'язка до ряду
        seat1 = Seats.objects.create(number=2, raw=raw)

        # Видалення екземпляру моделі з бази даних
        hall.delete()

        # Перевірка того, що екземпляр моделі був видалений з бази даних
        with self.assertRaises(Hall.DoesNotExist):
            Hall.objects.get(id=hall.id)


class HallModelUniqueTestCase(TestCase):

    def setUp(self):
        self.cinema1 = Cinema.objects.create(name='Кінотеатр 1')
        self.cinema2 = Cinema.objects.create(name='Кінотеатр 2')
        self.hall1 = Hall.objects.create(name='Зал 1', cinema=self.cinema1)

    def test_unique_together(self):
        # Перевіряємо, що не можна створити зал з таким самим ім'ям та для того ж кінотеатру
        with transaction.atomic():
            with self.assertRaises(IntegrityError) as context:
                Hall.objects.create(name='Зал 1', cinema=self.cinema1)
        self.assertTrue('unique constraint' in str(context.exception))

            # Перевіряємо, що можна створyesити зал з таким самим ім'ям, але для іншого кінотеатру
        with transaction.atomic():
            hall2 = Hall.objects.create(name='Зал 1', cinema=self.cinema2)
            self.assertIsNotNone(hall2.id)


class RawModelUniqueTest(TestCase):

    def setUp(self):
        self.cinema = Cinema.objects.create(name='Кінотеатр')
        self.cinema1 = Cinema.objects.create(name='Кінотеатр 1')
        self.hall = Hall.objects.create(name='Зал', cinema=self.cinema)
        self.hall1 = Hall.objects.create(name='Зал', cinema=self.cinema1)
        self.raw1 = Raw.objects.create(number=1, hall=self.hall)

    def test_unique_together(self):
        # Перевіряємо, що не можна створити ряд з таким самим номером та для того ж залу
        with transaction.atomic():
            with self.assertRaises(IntegrityError) as context:
                Raw.objects.create(number=1, hall=self.hall)
        self.assertTrue('unique constraint' in str(context.exception))

        # Перевіряємо, що можна створити ряд з таким самим номером, але для іншого залу
        with transaction.atomic():
            hall2 = Hall.objects.create(name='Інший зал', cinema=self.cinema)
            raw2 = Raw.objects.create(number=1, hall=hall2)
        self.assertIsNotNone(raw2.id)

        # Перевіряємо, що можна створити ряд з іншим номером, але для того ж залу
        with transaction.atomic():
            raw3 = Raw.objects.create(number=2, hall=self.hall)
        self.assertIsNotNone(raw3.id)

    def test_unique(self):

        # Перевіряємо, що можна створити ряд з таким самим номером, з атким саме залом  але для іншого кінотеатру
        with transaction.atomic():
            raw2 = Raw.objects.create(number=1, hall=self.hall1)
        self.assertIsNotNone(raw2.id)

class RawModelBaseTest(TestCase):

    def setUp(self):
        self.cinema = Cinema.objects.create(name='Кінотеатр')
        self.hall = Hall.objects.create(name='Зал', cinema=self.cinema)
        self.raw = Raw.objects.create(number=1, hall=self.hall)

    def test_add_sets(self):
        # Перевіряємо, що можна створити набір місць для ряду
        num = 5
        sets = self.raw.add_sets(num, Seats)
        self.assertEqual(sets, num)

        # Перевіряємо, що місця були створені для відповідного ряду
        raw_sets = Seats.objects.filter(raw=self.raw).order_by('number')
        self.assertEqual(len(raw_sets), num)
        self.assertEqual(raw_sets[0].number, 1)

        # Перевіряємо, що місця були створені з номерами від 1 до num
        for idx, set in enumerate(raw_sets):
            self.assertEqual(set.number, idx+1)

    def test_str(self):
        # Перевіряємо, що метод __str__ повертає очікуваний рядок
        expected_str = f"Ряд: {self.raw.number}"
        self.assertEqual(str(self.raw), expected_str)

from django.test import TestCase
from .models import Seats, Raw, Hall, Cinema

class SeatsModelTest(TestCase):

    def setUp(self):
        self.cinema = Cinema.objects.create(name='Кінотеатр')
        self.hall = Hall.objects.create(name='Зал', cinema=self.cinema)
        self.raw = Raw.objects.create(number=1, hall=self.hall)
        self.seat = Seats.objects.create(number=1, raw=self.raw)

    def test_str(self):
        # Перевіряємо, що метод __str__ повертає очікуваний рядок
        expected_str = str(self.cinema) + str(self.hall) + str(self.raw) + str(self.seat.number)
        self.assertEqual(str(self.seat), expected_str)
