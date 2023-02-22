from rest_framework import generics
from rest_framework.response import Response
from poll.models.poll import Poll
from poll.permissions import IsPollOwnerOrReadOnly, IsPollRedactor
from poll.serializers_v2.poll import PollSerializer


class PollViewSet(generics.CreateAPIView,
                  generics.UpdateAPIView,
                  generics.DestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsPollOwnerOrReadOnly | IsPollRedactor]

    def get_serializer_context(self):
        return {
            'request': self.request
        }

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({'result': 'ok'})

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)
