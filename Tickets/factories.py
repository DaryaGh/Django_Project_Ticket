import factory
import random
from django.utils import timezone
from django.contrib.auth.models import User
from faker import Faker
from factory.django import DjangoModelFactory
from .models import *
from .Choices import PRIORITY_CHOICES,STATUS_CHOICES,EMAIL_CHOICES


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    # username =factory.Sequence(lambda n:f"user{n}")
    username = factory.faker.Faker('user_name')
    # email = factory.faker.Faker('email')
    # email = factory.LazyAttribute(lambda obj:f'{obj.username}@example.com')
    email = factory.LazyAttribute(
        lambda obj: f"{obj.username}@{random.choice([choice[0] for choice in EMAIL_CHOICES])}"
    )
    password = factory.PostGenerationMethodCall('set_password', "password123")
    last_login = factory.Faker('date_time_this_decade', tzinfo=timezone.get_current_timezone())
    is_active = factory.Faker('boolean')

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    # name = factory.faker.Faker("name")
    # name = factory.Sequence(lambda n: slugify(n))
    # name = factory.lazy_attribute(lambda o: o.name.capitalize())
    name = factory.Faker('name')
    is_active = factory.Faker('boolean')
    # created_at = factory.Faker('date_time')
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='+30d')
    # updated_at = factory.Faker('date_time')
    updated_at = factory.Faker('date_time_between', start_date='-60d', end_date='+60d')

class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag


    # name = factory.Faker('word', locale='fa')
    name = factory.Faker('name', locale='fa')
    # name = factory.lazy_attribute_sequence(lambda obj , n:f"{factory.Faker('word')}-{factory.Faker('word')} {n:03d}")

class TicketFactory(DjangoModelFactory):
    class Meta:
        model = Ticket

    category = factory.SubFactory(CategoryFactory)
    created_by = factory.SubFactory(UserFactory)
    priority = factory.Iterator([choice[0] for choice in PRIORITY_CHOICES])
    subject = factory.Faker('sentence',nb_words=12)
    description = factory.Faker('paragraph')
    max_replay_date = factory.Faker('future_datetime',tzinfo=timezone.get_current_timezone())

class AssignmentFactory(DjangoModelFactory):
    class Meta:
        model = Assignment

    assigned_ticket = factory.LazyAttribute(lambda o: Ticket.objects.order_by('?').first())
    assignee = factory.LazyAttribute(lambda o: User.objects.order_by('?').first())
    seen_at = factory.Faker('future_datetime', tzinfo=timezone.get_current_timezone())
    status = factory.Iterator([choice[0] for choice in STATUS_CHOICES])
    description = factory.Faker('sentence')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj, created = Assignment.objects.get_or_create(
            assigned_ticket=kwargs.get('assigned_ticket'),
            assignee=kwargs.get('assignee'),
            defaults={
                'seen_at': kwargs.get('seen_at'),
                'status': kwargs.get('status'),
                'description': kwargs.get('description')
            }
        )
        return obj

# class AssignmentFactory(DjangoModelFactory):
#     class Meta:
#         model = Assignment
#
#     # assigned_ticket = factory.SubFactory(TicketFactory)
#     assigned_ticket = factory.Iterator(Ticket.objects.all())
#     # assignee = factory.SubFactory(UserFactory)
#     assignee = factory.Iterator(User.objects.all())
#     seen_at = factory.Faker('future_datetime',tzinfo=timezone.get_current_timezone())
#     status = factory.Iterator([choice[0] for choice in STATUS_CHOICES])
#     description = factory.Faker('sentence')
