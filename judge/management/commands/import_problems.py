import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from judge.models import Language, Problem, ProblemGroup, ProblemType, Profile


class Command(BaseCommand):
    help = 'Nap bai tap tu file data.json vao database'

    def add_arguments(self, parser):
        parser.add_argument('json_path', help='Duong dan toi data.json')
        parser.add_argument('--author', default=None,
                            help='Username lam tac gia bai')
        parser.add_argument('--public', action='store_true',
                            help='Cho bai hien cong khai ngay')

    def handle(self, *args, **options):
        with open(options['json_path'], encoding='utf-8') as f:
            items = json.load(f)

        group, _ = ProblemGroup.objects.get_or_create(
            name='uncategorized', defaults={'full_name': 'Uncategorized'})
        ptype, _ = ProblemType.objects.get_or_create(
            name='uncategorized', defaults={'full_name': 'Uncategorized'})

        languages = list(Language.objects.all())
        if not languages:
            self.stderr.write('Khong co ngon ngu nao trong DB. Dung lai.')
            return

        author = None
        if options['author']:
            author = Profile.objects.filter(
                user__username=options['author']).first()
            if author is None:
                self.stderr.write('Khong tim thay user %s. Dung lai.'
                                  % options['author'])
                return

        n_new = n_upd = 0
        for it in items:
            defaults = {
                'name': it['name'],
                'description': it['description'],
                'time_limit': it['time_limit'],
                'memory_limit': it['memory_limit'],
                'points': it['points'],
                'partial': True,
                'group': group,
                'is_public': options['public'],
                'date': timezone.now(),
            }
            problem, is_new = Problem.objects.update_or_create(
                code=it['code'], defaults=defaults)

            problem.types.set([ptype])
            problem.allowed_languages.set(languages)
            if author:
                problem.authors.set([author])

            if is_new:
                n_new += 1
            else:
                n_upd += 1

        self.stdout.write('Xong. Tao moi: %d, cap nhat: %d' % (n_new, n_upd))
