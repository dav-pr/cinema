from django.db import models
from django.utils.text import slugify


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
        verbose_name_plural = "Кінотеатр"
        verbose_name = "Кінотеатри"

    def __str__(self) -> str:
        """
        :return: найменування кінотеатру та його адресу
        """
        return f'{self.name} адреса: {self.address}'

    def save(self, *args, **kwargs):
        "метод створює слаг-атрибут з імені кінотеатру"
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs) -> None:
        """
        Метолд здійснює перевірку наявності дублікатів кінотеатру про критерію "імені" та "адреси".
        Перевірка здійснюється незалежно від регістра написання найменування кінотеатру та адреси.
        Враховуючи, що атрибути об'єкту "Кінотеатр" зберігаються з урахуванням регістру, то здійснюється
        приведення таких атрибутів та вхідних параметрів до одного регістра - lower().
        Також, з метою запобігання виникнення рекурсії в коді "for el in Cinema.objects.all():" здійснюється
        перевірка способу виклику конструктора: "if name != '' and address !='':".
        :param args:
        :param kwargs: має містити параметри "name" та "address"
        """
        name = kwargs.get('name', '').lower()
        address = kwargs.get('address', '').lower()
        # Перевірка наявності дублікатів
        if name != '' and address !='':
            for el in Cinema.objects.all():
                name_inst=str(el.name)
                address_inst=str(el.address)
                if name_inst.lower() == name or address_inst.lower() == address:
                    raise IntegrityError('UNIQUE constraint')
        super().__init__(*args, **kwargs)



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
        verbose_name_plural = "Зал"
        verbose_name = "Зали"

    def capacity(self):
        "Метод обчислює місткість кінозалу"
        capacity = 0
        for raw in self.raw_set.all():
            for seat in raw.seats_set.all():
                capacity += 1
        return capacity


class Raw(models.Model):
    number = models.PositiveIntegerField()
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)

    class Meta:
        ordering = ["number"]
        unique_together = ('number', 'hall')
        verbose_name_plural = "Ряд"
        verbose_name = "Ряди"

    def __str__(self):
        return f"Ряд: {self.number}"

    def add_sets(self, num, obj):
        for idx in range(1, num + 1):
            obj.objects.create(number = idx, raw = self)
        return num



class Seats(models.Model):
    number = models.PositiveIntegerField()
    raw = models.ForeignKey(Raw, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('number', 'raw')
        verbose_name_plural = "Місце"
        verbose_name = "Місця"

    def __str__(self):
        res = str(self.raw.hall.cinema)
        res += str(self.raw.hall)
        res += str(self.raw)
        res += str(super())
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
