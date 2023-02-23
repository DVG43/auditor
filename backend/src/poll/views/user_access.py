from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from poll.query import get_or_404, get_or_none
from poll.models.poll import Poll
from poll.models.user_access import UserAccess, Invitations
from poll.serializers.user_access import UserAccessRequestSerializer, UserAccessSerializer, InvitationSerializer


User = get_user_model()


class UserAccessView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserAccessRequestSerializer
        return UserAccessSerializer

    def get_serializer_context(self):
        poll_id = self.request.parser_context['kwargs'].get('pk')
        poll = get_or_404(Poll, pk=poll_id, error_msg='Poll not found')
        return {'poll': poll, 'request': self.request}

    def get_object(self):
        poll_id = self.request.parser_context['kwargs'].get('pk')
        email = self.request.data['email']

        obj = get_or_none(UserAccess, poll_id=poll_id, user__email=email)
        if not obj:
            obj = get_or_404(Invitations, poll_id=poll_id, email=email)
            self.serializer_class = InvitationSerializer
        return obj

    def list(self, request, *args, **kwargs):
        poll_id = self.request.parser_context['kwargs'].get('pk')
        result = []
        user_access_queryset = UserAccess.objects.filter(poll_id=poll_id)
        invitations_queryset = Invitations.objects.filter(poll_id=poll_id)

        user_access_serializer = UserAccessSerializer(user_access_queryset, many=True)
        invitations_serializer = InvitationSerializer(invitations_queryset, many=True)

        result.extend(user_access_serializer.data)
        result.extend(invitations_serializer.data)
        return Response(result)

    def delete(self, request, *args, **kwargs):
        super(UserAccessView, self).delete(request, *args, **kwargs)
        return Response({'result': 'access closed successfully'})


class TransferAccess(APIView):
    def post(self, request, pk):
        poll = get_or_404(Poll, pk=pk, error_msg='Poll is not found')
        if all([request.user != poll.owner, not request.user.is_staff]):
            raise PermissionDenied()
        user_id = request.data.get('user_id', None)
        new_user = get_or_404(User, pk=user_id, error_msg='User is not found')
        poll.owner = new_user
        poll.save()
        return Response({'result': 'rights have been successfully transferred'})

