from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from django.test import TestCase
from django.db import transaction
from datetime import date, timedelta, datetime
from datetime import date
from django.utils import timezone
from django.utils.timezone import make_aware, get_default_timezone, get_current_timezone
from zoneinfo import ZoneInfo

from .models import Movie, Screening, Ticket, PriceZone, create_tickets
from base.models import Cinema, Hall


class MovieModelTest(TestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            title='Test Movie',
            release_date=date.today(),
            director='Test Director',
            description='This is a test movie',
            poster='poster/test_movie.jpg',
            imdb_ukr='https://www.imdb.com/title/tt1234567/',
            duration=120,
            start_date_right_to_rent=date.today(),
            end_date_right_to_rent=date.today() + timedelta(days=15)
        )

    def test_movie_title(self):
        self.assertEqual(self.movie.title, 'Test Movie')

    def test_movie_release_date(self):
        self.assertEqual(self.movie.release_date, date.today())

    def test_movie_director(self):
        self.assertEqual(self.movie.director, 'Test Director')

    def test_movie_description(self):
        self.assertEqual(self.movie.description, 'This is a test movie')

    def test_movie_poster(self):
        self.assertEqual(self.movie.poster, 'poster/test_movie.jpg')

    def test_movie_imdb_ukr(self):
        self.assertEqual(self.movie.imdb_ukr, 'https://www.imdb.com/title/tt1234567/')

    def test_movie_duration(self):
        self.assertEqual(self.movie.duration, 120)

    def test_movie_start_date_right_to_rent(self):
        self.assertEqual(self.movie.start_date_right_to_rent, date.today())

    def test_movie_end_date_right_to_rent(self):
        self.assertEqual(self.movie.end_date_right_to_rent, date.today() + timedelta(days=15))

    def test_movie_slug(self):
        self.assertEqual(self.movie.slug, 'test-movie')

    def test_movie_unique_together(self):
        with self.assertRaises(IntegrityError):
            Movie.objects.create(
                title='Test Movie',
                release_date=date.today(),
                director='Test Director',
                description='This is a test movie',
                poster='poster/test_movie.jpg',
                imdb_ukr='https://www.imdb.com/title/tt1234567/',
                duration=120,
                start_date_right_to_rent=date.today(),
                end_date_right_to_rent=date.today()
            )

    def test_movie_string_representation(self):
        self.assertEqual(str(self.movie), 'Test Movie')

    def test_movie_requed_value(self):
        dict = {'title': 'Test Movie',
                'release_date': '01.01.2023',
                "director": 'Test Director',
                "description": 'This is a test movie',
                "poster": 'poster/test_movie.jpg',
                "imdb_ukr": "https://www.imdb.com/title/tt1234567/",
                "duration": "120",
                "start_date_right_to_rent": '01.01.2023',
                "end_date_right_to_rent": '01.04.2023'
                }
        for key in list(dict.keys()):
            del dict[key]
            with transaction.atomic():
                with self.assertRaises(ValueError):
                    Movie.objects.create(**dict)


class MovieModelSaveTestCase(TestCase):

    def setUp(self):
        self.movie_data = {
            'title': 'Test Movie',
            'release_date': date(2022, 4, 1),
            'director': 'Test Director',
            'description': 'Test Description',
            'duration': 120,
            'start_date_right_to_rent': date.today(),
            'end_date_right_to_rent': date.today() + timedelta(days=15),
        }

    def test_save_method(self):
        movie = Movie(**self.movie_data)
        movie.save()
        self.assertIsNotNone(movie.slug)

        # Test that the slug is created correctly
        expected_slug = 'test-movie'
        self.assertEqual(movie.slug, expected_slug)

        # Test that a ValueError is raised if required fields are empty
        movie.title = ''
        with self.assertRaises(ValueError):
            movie.save()


class MovieUniqModelTests(TestCase):
    def setUp(self):
        self.movie1 = Movie.objects.create(
            title='The Godfather',
            release_date='1972-03-24',
            director='Francis Ford Coppola',
            description='An organized crime dynasty',
            poster='poster/godfather.jpg',
            imdb_ukr='https://www.imdb.com/title/tt0068646/',
            duration=175,
            start_date_right_to_rent='2023-03-01',
            end_date_right_to_rent='2023-03-31',
        )

    def test_duplicate_movie_raises_error(self):
        with self.assertRaises(IntegrityError):
            Movie.objects.create(
                title='The Godfather',
                release_date='1972-03-24',
                director='Francis Ford Coppola',
                description='An organized crime dynasty',
                poster='poster/godfather.jpg',
                imdb_ukr='https://www.imdb.com/title/tt0068646/',
                duration=175,
                start_date_right_to_rent='2023-03-01',
                end_date_right_to_rent='2023-03-31',
            )


class ScreeningModelTestCase(TestCase):
    def setUp(self):
        cinema = Cinema.objects.create(name='Кінотеатр', address="вул. Шевченка 1")
        self.hall = Hall.objects.create(name='Зал 1', cinema=cinema)
        self.movie = Movie.objects.create(title='The Godfather',
                                          release_date='1972-03-24',
                                          director='Francis Ford Coppola',
                                          description='An organized crime dynasty',
                                          poster='poster/godfather.jpg',
                                          imdb_ukr='https://www.imdb.com/title/tt0068646/',
                                          duration=175,
                                          start_date_right_to_rent=timezone.now() - timedelta(days=1),
                                          end_date_right_to_rent=timezone.now() + timedelta(days=30))

    def test_screening_creation(self):
        start_time = timezone.now() + timedelta(hours=1)
        screening = Screening.objects.create(hall=self.hall, movie=self.movie,
                                             start_time=start_time)
        self.assertEqual(screening.hall, self.hall)
        self.assertEqual(screening.movie, self.movie)
        self.assertEqual(screening.start_time, start_time)

    def test_screening_creation_time_overlap(self):
        start_time = timezone.now()
        screening1 = Screening.objects.create(hall=self.hall, movie=self.movie,
                                              start_time=start_time)
        screening1.clean_start_time()
        screening1.save()
        with self.assertRaises(ValidationError):
            screening2 = Screening.objects.create(hall=self.hall, movie=self.movie,
                                                  start_time=screening1.start_time + timedelta(minutes=30))
            screening2.clean_start_time()

    def test_screening_creation_time_right_to_rent(self):
        with self.assertRaises(ValidationError):
            screening = Screening.objects.create(hall=self.hall, movie=self.movie,
                                                 start_time=self.movie.end_date_right_to_rent + timedelta(minutes=30))
            screening.clean_start_time()

    def test_str_method(self):
        self.screening = Screening.objects.create(
            hall=self.hall,
            movie=self.movie,
            start_time=timezone.now(),
            price_zone=None
        )
        expected_str = f"{self.screening.movie} at {self.screening.hall.cinema} {self.screening.hall} on {self.screening.start_time}"
        self.assertEqual(str(self.screening), expected_str)


class TicketModelTestCase(TestCase):
    def setUp(self):
        # створення тестових об'єктів
        self.cinema = Cinema.objects.create(name='Кінотеатр', address="вул. Шевченка 1")
        self.hall = Hall.objects.create(name='Зал 1', cinema=self.cinema)
        self.hall.fill_hall(10, 12, 12, 12, 15, 16, 18, 25)

        self.movie = Movie.objects.create(title='The Godfather',
                                          release_date='1972-03-24',
                                          director='Francis Ford Coppola',
                                          description='An organized crime dynasty',
                                          poster='poster/godfather.jpg',
                                          imdb_ukr='https://www.imdb.com/title/tt0068646/',
                                          duration=175,
                                          start_date_right_to_rent=timezone.now() - timedelta(days=1),
                                          end_date_right_to_rent=timezone.now() + timedelta(days=30))

        dt = datetime(2023, 3, 15, 14, 30, 0, tzinfo=ZoneInfo('Europe/Kiev'))
        self.screening = Screening.objects.create(hall=self.hall, movie=self.movie,
                                                  start_time=dt)
        self.ticket = Ticket.create(screening=self.screening, seat=1, raw=1, price=Decimal('150.00'))
        self.ticket.save()

    def test_ticket_str_method(self):
        # створення об'єкту Ticket
        ticket = Ticket.create(screening=self.screening, seat=1, raw=1, price=Decimal('150.00'))
        # перевірка __str__ методу
        self.assertEqual(str(ticket),
                         " The Godfather Сеанс: 15.03.2023 14:30 Кінотеатр адреса: вул. Шевченка 1 Зал:Зал 1 Ряд: 1 Місце: 1")

    def test_ticket_unique_constraint(self):
        # створення другого об'єкту з тими самими значеннями для screening та seat
        ticket1 = Ticket.create(screening=self.screening, seat=1, raw=1, price=Decimal('120.00'))
        # перевірка, що збереження об'єкту викличе IntegrityError, оскільки комбінація screening та seat має бути унікальною
        with self.assertRaises(IntegrityError):
            ticket1.save()

    def test_create_ticket(self):
        count = Ticket.objects.count()
        # Створюємо квиток за допомогою методу менеджера
        ticket = Ticket.objects.create_ticket(screening=self.screening, seat=1, raw=2, price=Decimal('150.00'))
        # Перевіряємо, що квиток був створений і збережений в базі даних
        self.assertEqual(Ticket.objects.count(), count+1)
        self.assertEqual(ticket, Ticket.objects.last())


class ScreeningSignalTestCase(TestCase):
    def setUp(self):
        self.cinema1 = Cinema.objects.create(name='Кінотеатр 1', address='вул. Богдана Хмельницького, 24')
        hall = Hall.create(name='Зал 1', cinema=self.cinema1)
        hall.save()
        hall.fill_hall(10,10,10,10,10,10)

        movie = Movie.objects.create(
            title='Test Movie',
            release_date=date.today(),
            director='Test Director',
            description='This is a test movie',
            poster='poster/test_movie.jpg',
            imdb_ukr='https://www.imdb.com/title/tt1234567/',
            duration=120,
            start_date_right_to_rent=date.today(),
            end_date_right_to_rent=date.today() + timedelta(days=15)
        )

        price_zone = PriceZone.objects.create(name="Zone 1", price=150.0)
        self.screening = Screening.objects.create(hall=hall, movie=movie, start_time=timezone.now(), price_zone=price_zone)

    def test_create_tickets(self):
        create_tickets(sender=Screening, instance=self.screening, created=True, price=self.screening.price_zone.price)
        self.assertEqual(Ticket.objects.filter(screening = self.screening).count(), self.screening.hall.capacity())



