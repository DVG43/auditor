from http import HTTPStatus

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from poll.query import get_or_404
from poll.models.questions import ItemQuestion, ManyFromListQuestion, MediaItemQuestion, MediaQuestion, YesNoQuestion, \
    ItemsFreeAnswer, FreeAnswer
from poll.permissions import check_question_permission, check_item_permission
from poll.serializers.questions import ItemQuestionSerializer, MediaItemQuestionSerializer, ItemsFreeAnswerSerializer
from poll.service import update_order_yes_no_answer_items, update_order_free_answer_items


class ItemQuestionCollection(APIView):
    def put(self, request, pk, format=None):
        item_question = get_or_404(ItemQuestion, item_question_id=pk)
        check_item_permission(item=item_question, request=request)
        old_order_id = item_question.order_id

        serializer = ItemQuestionSerializer(item_question, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        item_question.normalize_order_id_other(
            old_order_id=old_order_id,
            new_order_id=item_question.order_id
        )
        update_order_yes_no_answer_items(
            item_question_id=pk, old_order_id=old_order_id, order_id=item_question.order_id
        )

        return Response({'result': serializer.data}, status=HTTPStatus.OK)

    def post(self, request, pk):
        question = get_or_404(ManyFromListQuestion, question_id=pk, error_msg={'result': 'ManyFromListQuestion is not found'})
        check_question_permission(poll=question.poll, request=request)
        if type(request.data) is list:
            serializer = ItemQuestionSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            for item in serializer.instance:
                question.items.add(item)
        else:
            serializer = ItemQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            question.items.add(serializer.instance)
        ItemQuestion.normalize_order_id(question.items)
        return Response({'result': serializer.data}, status=HTTPStatus.OK)

    def delete(self, request, pk, format=None):
        item = ItemQuestion.objects.filter(item_question_id=pk).first()
        check_item_permission(item=item, request=request)
        count = item.delete()
        if count == 0:
            return Response({'result': 'This item question is not found'}, status=HTTPStatus.NOT_FOUND)
        return Response({'result': 'The item question has been deleted'}, status=HTTPStatus.OK)


class MediaItemQuestionCollection(APIView):

    def put(self, request, pk, format=None):

        try:
            item_question = MediaItemQuestion.objects.get(media_question_id=pk)
            item_question = MediaItemQuestionSerializer().update(item_question, request.data)
            serialized_item_question = MediaItemQuestionSerializer(item_question)

            if item_question:
                return Response({'result': serialized_item_question.data}, status=HTTPStatus.OK)
            else:
                raise Exception('Bad request')

        except MediaItemQuestion.DoesNotExist:
            return Response({'result': 'Not found'}, status=HTTPStatus.NOT_FOUND)
        except Exception as er:
            return Response({'error': '{}'.format(er)}, status=HTTPStatus.BAD_REQUEST)

    def post(self, request,  pk, format=None):

        try:

            question = MediaQuestion.objects.get(question_id=pk)
            new_item_question = MediaItemQuestionSerializer(data=request.data)
            if new_item_question.is_valid():
                new_item_question.save()

            question.items.add(new_item_question.instance)
            question.save()

            item_question = MediaItemQuestionSerializer(new_item_question.instance)
            return Response({'result': item_question.data}, status=HTTPStatus.OK)

        except MediaItemQuestion.DoesNotExist:
            return Response({'result': 'MediaItemQuestion is not found'}, status=HTTPStatus.NOT_FOUND)
        except Exception as er:
            return Response({'error': '{}'.format(str(er))}, status=HTTPStatus.BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            count = MediaItemQuestion.objects.filter(media_question_id=pk).delete()

            if count == 0:
                return Response({'result': 'This media item question is not found'}, status=HTTPStatus.NOT_FOUND)

        except Exception as er:
            return Response({'error': str(er)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The item question has been deleted'}, status=HTTPStatus.OK)


class YesNoItemCollection(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    serializer_class = ItemQuestionSerializer
    queryset = ItemQuestion.objects.all()
    lookup_field = 'pk'

    def create(self, request, pk, *args, **kwargs):
        question = get_object_or_404(YesNoQuestion.objects.all(), question_id=pk)

        if type(request.data) is list:
            serializer = ItemQuestionSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            for item in serializer.instance:
                question.items.add(item)

        else:
            serializer = ItemQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            question.items.add(serializer.instance)

        question.save()
        ItemQuestion.normalize_order_id(question.items)
        headers = self.get_success_headers(serializer.data)
        return Response({'result': serializer.data}, status=HTTPStatus.OK, headers=headers)

    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_order_id = instance.order_id

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.normalize_order_id_other(
            old_order_id=old_order_id,
            new_order_id=instance.order_id
        )
        return Response({'result': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'result': 'The item question has been deleted'}, status=HTTPStatus.OK)


class FreeAnswerItemCollection(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    serializer_class = ItemsFreeAnswerSerializer
    queryset = ItemsFreeAnswer.objects.all()
    lookup_field = 'pk'

    def create(self, request, pk, *args, **kwargs):
        question = get_object_or_404(FreeAnswer.objects.all(), question_id=pk)

        if type(request.data) is list:
            serializer = ItemsFreeAnswerSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            for item in serializer.instance:
                question.items.add(item)

        else:
            serializer = ItemsFreeAnswerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            question.items.add(serializer.instance)

        question.save()
        headers = self.get_success_headers(serializer.data)
        return Response({'result': serializer.data}, status=HTTPStatus.OK, headers=headers)

    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_order_id = instance.order_id

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.normalize_order_id_other(
                old_order_id=old_order_id,
                new_order_id=instance.order_id
            )

        update_order_free_answer_items(
            item_question_id=pk, old_order_id=old_order_id, order_id=instance.order_id
        )

        return Response({'result': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'result': 'The item question has been deleted'}, status=HTTPStatus.OK)
