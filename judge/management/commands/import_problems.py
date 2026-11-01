import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from judge.models import Language, Problem, ProblemGroup, ProblemType, Profile

GROUP_LABEL = {
    'easy': 'Easy',
    'medium': 'Medium',
    'hard': 'Hard',
    'uncategorized': 'Uncategorized',
}


class Command(BaseCommand):
    help = 'Nap bai tap tu file data.json vao database'

    def add_arguments(self, parser):
        parser.add_argument('json_path')
        parser.add_argument('--author', default=None)
        parser.add_argument('--public', action='store_true')

    def handle(self, *args, **options):
        with open(options['json_path'], encoding='utf-8') as f:
            items = json.load(f)

        languages = list(Language.objects.all())
        if not languages:
            self.stderr.write('Khong co ngon ngu nao trong DB. Dung lai.')
            return

        author = None
        if options['author']:
            author = Profile.objects.filter(
                user__username=options['author']).first()
            if author is None:
                self.stderr.write('Khong tim thay user. Dung lai.')
                return

        groups, types = {}, {}

        def get_group(key):
            if key not in groups:
                groups[key], _ = ProblemGroup.objects.get_or_create(
                    name=key, defaults={'full_name': GROUP_LABEL.get(key, key.title())})
            return groups[key]

        def get_type(label):
            if label not in types:
                slug = label.lower().replace(' & ', '-').replace(' ', '-')
                types[label], _ = ProblemType.objects.get_or_create(
                    name=slug, defaults={'full_name': label})
            return types[label]

        n_new = n_upd = 0
        for it in items:
            problem, is_new = Problem.objects.update_or_create(
                code=it['code'],
                defaults={
                    'name': it['name'],
                    'description': it['description'],
                    'time_limit': it['time_limit'],
                    'memory_limit': it['memory_limit'],
                    'points': it['points'],
                    'partial': True,
                    'group': get_group(it.get('group', 'uncategorized')),
                    'is_public': options['public'],
                    'date': timezone.now(),
                })

            problem.types.set([get_type(t) for t in it.get('types', ['Uncategorized'])])
            problem.allowed_languages.set(languages)
            if author:
                problem.authors.set([author])

            if is_new:
                n_new += 1
            else:
                n_upd += 1

        self.stdout.write('Xong. Tao moi: %d, cap nhat: %d' % (n_new, n_upd))
