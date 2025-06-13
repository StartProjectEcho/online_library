# tasks.py
import pandas as pd
from celery import shared_task
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from books.models import Book, BookStatus
from recommendations.models import RecommendedBook
from reviews.models import Review
from users.models import CustomUser


@shared_task
def generate_recommendations_for_user(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return

    # Оптимизированный сбор данных о взаимодействиях
    interactions = {}
    reviews = Review.objects.filter(user=user).select_related('book', 'book__author')
    statuses = BookStatus.objects.filter(user=user).select_related('book')

    for review in reviews:
        interactions[review.book_id] = review.rating / 5.0

    for status in statuses:
        if status.status == 'favorite':
            interactions[status.book_id] = max(interactions.get(status.book_id, 0), 0.8)
        elif status.status == 'read':
            interactions[status.book_id] = max(interactions.get(status.book_id, 0), 0.6)

    abandoned_ids = set(BookStatus.objects.filter(
        user=user,
        status='abandoned'
    ).values_list('book_id', flat=True))

    if not interactions:
        return

    # Подготовка данных для TF-IDF
    books_data = Book.objects.exclude(id__in=abandoned_ids).prefetch_related('genres', 'authors').values(
        'id', 'genres__name', 'authors__name', 'description'
    )

    # Формируем DataFrame
    data = []
    for book in books_data:
        genres = ' '.join(book['genres__name'])
        authors = ' '.join(book['authors__name'])
        description = book['description'] or ''
        data.append({
            'id': book['id'],
            'features': f"{genres} {authors} {description}"
        })

    df = pd.DataFrame(data)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Генерация рекомендаций
    sim_scores = []
    for idx in df.index:
        if df.iloc[idx]['id'] in interactions:
            sim_scores.extend(list(enumerate(cosine_sim[idx])))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [(i, score) for i, score in sim_scores if df.iloc[i]['id'] not in interactions]
    sim_scores = sim_scores[:10]

    # Сохранение рекомендаций
    RecommendedBook.objects.filter(user=user).delete()
    for i, _ in sim_scores:
        RecommendedBook.objects.create(
            book_id=df.iloc[i]['id'],
            user=user,
            score=sim_scores[i][1]
        )

@shared_task
def generate_recommendations_for_all_users():
    users = CustomUser.objects.values_list('id', flat=True)
    for user_id in users:
        generate_recommendations_for_user.delay(user_id)


@shared_task
def update_global_recommendations():
    # Получаем все книги
    books = Book.objects.all()

    # Подготовка данных для TF-IDF
    data = []
    for book in books:
        genres = ' '.join([g.name for g in book.genres.all()])
        authors = ' '.join([a.name for a in book.authors.all()])
        data.append({
            'id': book.id,
            'features': f"{genres} {authors} {book.description or ''}"
        })

    df = pd.DataFrame(data)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Генерация глобальных рекомендаций
    sim_scores = []
    for idx in df.index:
        sim_scores.extend(list(enumerate(cosine_sim[idx])))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    seen_books = set()
    unique_scores = []
    for i, score in sim_scores:
        book_id = df.iloc[i]['id']
        if book_id not in seen_books:
            seen_books.add(book_id)
            unique_scores.append((i, score))
    sim_scores = unique_scores[:10]

    # Сохранение рекомендаций
    RecommendedBook.objects.filter(is_global=True).delete()
    for i, _ in sim_scores:
        RecommendedBook.objects.create(
            book_id=df.iloc[i]['id'],
            is_global=True,
            score=sim_scores[i][1]
        )