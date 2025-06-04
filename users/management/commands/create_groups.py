from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Создаёт группы Библиотекарь и Читатель'

    def handle(self, *args, **kwargs):
        librarian_group, created = Group.objects.get_or_create(name='Библиотекарь')
        reader_group, created = Group.objects.get_or_create(name='Читатель')

        self.stdout.write(self.style.SUCCESS('Группы успешно созданы'))