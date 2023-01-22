from django.shortcuts import get_object_or_404

from reviews.models import Review, Title


class CurrentTitle:
    requires_context = True

    def __call__(self, serializer_field):
        title_id = (
            serializer_field.context.get('request').parser_context
            .get('kwargs').get('title_id')
        )
        return get_object_or_404(Title, id=title_id)


class CurrentReview:
    requires_context = True

    def __call__(self, serializer_field):
        title_id = (
            serializer_field.context.get('request').parser_context
            .get('kwargs').get('title_id')
        )
        review_id = (
            serializer_field.context.get('request').parser_context
            .get('kwargs').get('review_id')
        )
        return get_object_or_404(Review, title_id=title_id, id=review_id)
