from django.db import models

# Create your models here.

from django.db import models


class Cinema(models.Model):
    """
    Класс Cinema реалізує сутність "кінотеатру".
    Має такі атрібути:
    name: найменування кінотеатру
    address: адерса кінотеатру
    """
    name = models.CharField(max_length=32, null=False, blank=False, db_index=True)
    address = models.CharField(max_length=256, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Кінотеатр"
        verbose_name = "Кінотеатри"

    def __str__(self)-> str:
        """
        :return: найменування кінотеатру та його адресу
        """
        return f'{self.name} адреса: {self.address}'


class BasicSeat(models.Model):
    number = models.PositiveIntegerField()
    def __str__(self):
        return f"Місце: {self.number}"

    class Meta:
        abstract = True
        ordering = ["number"]
        verbose_name_plural = "Абстракте місце"
        verbose_name = "Абстракті Місця"

class BasicRaw(models.Model):

    number = models.PositiveIntegerField()
    size = models.PositiveIntegerField()

    class Meta:
        abstract = True
        ordering = ["name"]
        verbose_name_plural = "Абстрактний ряд"
        verbose_name = "Абстрактні ряди"

    def __str__(self):
        return f"Ряд: {self.number}"


class BasicHall(models.Model):

    name = models.CharField(max_length=16, null=False, blank=False, db_index=True)

    class Meta:
        abstract = True
        ordering = ["name"]
        verbose_name_plural = "Абстрактний зал"
        verbose_name = "Абстрактні зали"

    def __str__(self):
        return f"Зал: {self.name}"

class Hall(BasicHall):

    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Зал"
        verbose_name = "Зали"

    def capacity(self):
        capacity = 0
        for raw in self.raw.all():
            for seat in raw.seats.all():
                capacity +=1
        return capacity

class Raw(BasicRaw):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    class Meta:
        ordering = ["hall"]
        verbose_name_plural = "Ряд"
        verbose_name = "Ряди"

class Seats(BasicSeat):
    raw = models.ForeignKey(Raw, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Місце"
        verbose_name = "Місця"

    def __str__ (self):
        res = str(self.raw.hall.cinema)
        res += str (self.raw.hall)
        res += str(self.raw)
        res += str (super(self))
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
