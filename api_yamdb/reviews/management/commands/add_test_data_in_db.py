import csv
import logging
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import User

logger = logging.getLogger(__name__)

DATA_PATH = os.path.join(BASE_DIR, 'static/data')

FILES_MODELS = {
    'users.csv': get_user_model(),
    'category.csv': Category,
    'genre.csv': Genre,
    'titles.csv': Title,
    'genre_title.csv': TitleGenre,
    'review.csv': Review,
    'comments.csv': Comment,
}


class Command(BaseCommand):
    help = f'''This command helps to add test data from {DATA_PATH}
    in database. Don't forget to migrate before adding any information in db.
    '''

    def handle(self, *args, **options):
        for file_name in FILES_MODELS:
            file_path = os.path.join(DATA_PATH, file_name)
            model = FILES_MODELS.get(file_name)

            with open(file_path, mode='r') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    category = row.get('category')
                    author = row.get('author')
                    pub_date = row.get('pub_date')

                    if category:
                        row['category'] = (Category.objects.get(pk=category))
                    if author:
                        row['author'] = User.objects.get(pk=author)
                    if pub_date:
                        row.pop('pub_date')

                    try:
                        logger.info(model.objects.get_or_create(**row))
                    except Exception:
                        logger.error(file_path, model, row, exc_info=True)
