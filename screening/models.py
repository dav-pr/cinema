from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from unidecode import unidecode
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from base.models import Cinema, Hall, Seats


# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    release_date = models.DateField(null=False, blank=False)
    director = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    poster = models.ImageField(upload_to='poster/', null=False, blank=False)
    imdb_ukr = models.URLField(help_text= _("Посилання на сторінку IMDB з описом фільма"))
    duration = models.PositiveIntegerField()
    start_date_right_to_rent = models.DateField(help_text= _("Дата початку права на прокат"))
    end_date_right_to_rent = models.DateField(help_text= _("Дата закінчення права на прокат"))

    class Meta:
        unique_together = ('title', 'director')
        verbose_name_plural = _("Фільм")
        verbose_name = _("Фільми")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        "метод створює слаг-атрибут для найменування фільму"
        if self.title == '' or self.director == '' or self.description == '':
            raise ValueError
        self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

class PriceZone(models.Model):
    name = models.CharField(max_length=16, null=False, blank=False)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"


class Screening(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    price_zone = models.ForeignKey(PriceZone, on_delete=models.DO_NOTHING, default= None, null = True)

    def __str__(self):
        return f"{self.movie} at {self.hall.cinema} {self.hall} on {self.start_time}"

    def clean_start_time(self):
        movie_inst = self.movie
        if not (self.start_time >= movie_inst.start_date_right_to_rent  and self.start_time <= movie_inst.end_date_right_to_rent):
            raise ValidationError(_(f'Дата сеансу має бути у межах дати прокатних прав: {movie_inst.start_date_right_to_rent} - '
                                    f'movie_inst.end_date_right_to_rent'))
        screening_inst = Screening.objects.filter(hall = self.hall)
        duration = movie_inst.duration
        for obj in screening_inst:
            if obj.pk == self.pk:  # skip current instance being edited
                continue
            if not (self.start_time > (obj.start_time + timedelta(minutes=duration))):
                raise ValidationError(
                    _(f'Час сеансів в одному залі не повинен перетинатися'))

    def get_all_seats(self):
        return Seats.objects.filter(hall = self.hall)

    def get_sold_tickets(self):
        return Ticket.objects.filter(screening = self, is_sold = True)

    def get_not_sold_tickets(self):
        return Ticket.objects.filter(screening = self, is_sold = False)


    def get_sum_sold_tickets(self):
        self.get_sold_tickets().aggregate(Sum("price"))


class TicketManager(models.Manager):
    def create_ticket(self,  *args, **kwargs):
        row_num = kwargs.get('raw')
        seat_num = kwargs.get('seat')
        screening_inst = kwargs.get('screening')
        price = kwargs.get('price')
        seat_inst = Seats.objects.get(number=seat_num, raw=row_num, hall=screening_inst.hall)
        ticket = self.create(screening = screening_inst, seat = seat_inst, price = price)
        # do something with the book
        return ticket

class Ticket(models.Model):
    screening = models.ForeignKey(Screening, on_delete=models.DO_NOTHING, verbose_name=_('Сеанс'))
    seat = models.ForeignKey(Seats, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('Ціна'))
    is_sold = models.BooleanField(default = False)

    objects =  TicketManager()

    class Meta:
        unique_together = ('screening', 'seat')
        verbose_name = _('Квиток')
        verbose_name_plural = _('Квитки')

    @classmethod
    def create(cls,  *args, **kwargs):
        row_num = kwargs.get('raw')
        seat_num = kwargs.get('seat')
        screening_inst = kwargs.get('screening')
        price  = kwargs.get('price')
        seat_inst = Seats.objects.get(number = seat_num, raw = row_num, hall = screening_inst.hall)
        ticket = cls(screening = screening_inst,  seat = seat_inst , price = price)
        return ticket

    def __str__(self):
        dt = self.screening.start_time
        dt = dt.strftime('%d.%m.%Y %H:%M')
        return f' {self.screening.movie}'+ _(" Сеанс: ")+ f'{dt} {self.seat}'


@receiver(post_save, sender=Screening)
def create_tickets(sender, instance, created, **kwargs):
    if created:
        # Створюємо екземпляри Ticket
        price = kwargs.get('price', 0)
        if price !=0:
            with transaction.atomic():
                for seat in Seats.objects.filter(hall = instance.hall):
                    ticket = Ticket.create(screening=instance, seat=seat.number, raw = seat.raw, price = price)
                    ticket.save()
