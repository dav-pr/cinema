from django.db import models
from django.utils.text import slugify
from unidecode import unidecode
from django.utils.translation import gettext_lazy as _


# Create your models here.
from django.db.utils import IntegrityError


class Cinema(models.Model):
    """
    Класс Cinema реалізує сутність "кінотеатру".
    Має такі атрібути:
    name: найменування кінотеатру
    address: адреса кінотеатру
    """
    name = models.CharField(max_length=128, null=False, blank=False, db_index=True)
    address = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        unique_together = ('name', 'address')
        verbose_name_plural = _("Кінотеатр")
        verbose_name = _("Кінотеатри")

    @classmethod
    def create(cls, name, address):
        if not isinstance(name, str) or not isinstance(address, str) or name == '' or address== '':
            raise ValueError
        name = name.lower()
        address = address.lower()

        # Перевірка наявності дублікатів
        if name != '' and address != '':
            for el in Cinema.objects.all():
                name_inst = str(el.name)
                address_inst = str(el.address)
                if name_inst.lower() == name or address_inst.lower() == address:
                    raise IntegrityError('UNIQUE constraint')
        cinema = cls(name = name, address = address)
        return cinema

    def __str__(self) -> str:
        """
        :return: найменування кінотеатру та його адресу
        """
        return f'{self.name}'+ _(' адреса: ') + f'{self.address}'

    def save(self, *args, **kwargs):
        "метод створює слаг-атрибут з імені кінотеатру"
        if self.address == '':
            raise ValueError
        self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)




class Hall(models.Model):
    """
    Клас  Hall реалізіціє сутність "кінозал".
    Має атрибути:
    name: найменування зали
    cinema: посилання на кінотеатр, де знаходиться зал.
    Параметром unique_together = ('name', 'cinema') забезпечується унікальність найменувать залів в конкретному
    кінотеатру
    """
    name = models.CharField(max_length=16, null=False, blank=False, db_index=True)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)


    class Meta:
        unique_together = ('name', 'cinema')
        verbose_name_plural = _("Зал")
        verbose_name = _("Зали")

    @classmethod
    def create(cls, cinema, name):
        if name == '' or  (name is  None) or (cinema is None) or cinema=='':
            raise ValueError(_('Параметри cinema та/або name повинні мати значення'))
        hall = cls(cinema=cinema, name=name)
        return hall

    def __str__(self):
        return _('Зал:') + f'{self.name}'

    def capacity(self):
        "Метод обчислює місткість кінозалу"
        # capacity = 0
        # for raw in self.raw_set.all():
        #     for seat in raw.seats_set.all():
        #         capacity += 1
        # return capacity
        return Seats.objects.filter(hall=self).count()

    def fill_hall(self, *args):
        for num_row, number_of_seat_in_row in enumerate(args):
            for number_seat in range(1, number_of_seat_in_row + 1):
                seat = Seats.objects.create(number=number_seat, raw=num_row + 1, hall = self)
                seat.save()

    def get_num_of_row(self):
        return Seats.objects.filter(hall = self).distinct('raw').count()

    def get_num_of_sets_in_row(self, num_row):
        return Seats.objects.filter(hall=self, raw=num_row).count()



class Seats(models.Model):
    """
    Клас реалізує сутність категорії "Місце".
    Клас має такі атрибути:
        number - номер
        raw - ряд

    """
    number = models.PositiveIntegerField()
    raw = models.PositiveIntegerField()
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    # raw = models.ForeignKey(Raw, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('number', 'raw', 'hall')
        verbose_name_plural = _("Місце")
        verbose_name = _("Місця")

    def __str__(self):
        res = ' '.join((str(self.hall.cinema), str(self.hall), _("Ряд: ") + f"{self.raw}",
                       _("Місце: ") + f"{self.number}"))
        return res

# class PriceZone(models.Model):
#     name = models.CharField(max_length=16, null=False, blank=False)
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.name} - ${self.price:.2f}"
#
#
#
# class Movie(models.Model):
#     title = models.CharField(max_length=200)
#     release_date = models.DateField()
#     director = models.CharField(max_length=200)
#
#     def __str__(self):
#         return self.title
#
#
# class Screening(models.Model):
#     cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#
#     def __str__(self):
#         return f"{self.movie} at {self.cinema} on {self.start_time}"
