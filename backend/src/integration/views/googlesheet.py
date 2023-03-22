from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from http import HTTPStatus
from django.http import HttpResponseRedirect

from integration.serializers.googlesheet import GoogleSheetIntegrationSerializer
from integration.serializers.googlesheet import GoogleSheetIntegrationPatchSerializer
from integration.models.googlesheet import GoogleSheetIntegration, GoogleSheetCredentials

SESSION = {}


class GoogleSheetIntegrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be created, viewed, edited or deleted.
    """
    serializer_class = GoogleSheetIntegrationSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        queryset = GoogleSheetIntegration.objects.all().order_by('-id')
        return queryset

    def get_serializer_context(self):
        context = super(GoogleSheetIntegrationViewSet, self).get_serializer_context()
        context['poll_id'] = self.kwargs.get('poll_id')
        context['survey_id'] = self.kwargs.get('survey_id')
        context['user'] = self.request.user
        context['request'] = self.request
        return context

    def update(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(GoogleSheetIntegration, id=pk)
        credentials = get_object_or_404(GoogleSheetCredentials, user=instance.user)
        credentials.refresh_token(request)

        if credentials.google_sheet_credentials == '':
            instance.delete()
            credentials.delete()
            return Response(
                {'detail': 'The refresh token of GS API is dead. Make the new integration.'},
                status=HTTPStatus.SERVICE_UNAVAILABLE)

        request.session['gs_credentials'] = credentials.google_sheet_credentials

        return super(GoogleSheetIntegrationViewSet, self).update(request, pk, *args, **kwargs)

    def create(self, request):
        """
        Returns the authorization URL that redirects and continues the integration build.

        ---
        Request body:
        - id: poll_id
          required: true
          type: integer
        """
        if GoogleSheetIntegration.objects.filter(id=request.data['id']).exists():
            return Response({'detail': 'The GS Integration object is already exist.'},
                            status=HTTPStatus.BAD_REQUEST)

        SESSION['data'] = request.data
        SESSION['user'] = request.user

        authorization_url, state = GoogleSheetCredentials.get_google_auth_url(
            settings.CREDENTIALS_FILE_NAME)

        return Response(authorization_url)

    def partial_update(self, request, pk=None, *args, **kwargs):
        kwargs['partial'] = True

        instance = get_object_or_404(GoogleSheetIntegration, id=pk)
        serializer = GoogleSheetIntegrationPatchSerializer(instance, context={'request': request},
                                                           data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(pk, instance, *args, **kwargs)

        return Response(serializer.data)


class CreateGoogleSheetView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, request, **kwargs):
        user = SESSION.get('user', '')

        if user == '':
            return Response(
                {'detail': 'Need to authenticate before accessing this functional.'},
                status=HTTPStatus.UNAUTHORIZED)

        credentials, created = GoogleSheetCredentials.objects.get_or_create(user=user)
        credentials.create_connection(request, settings.CREDENTIALS_FILE_NAME)

        if credentials.google_sheet_credentials == '':
            return Response(
                {'detail': 'The connection with GS API is absent. Contact to the administrstor.'},
                status=HTTPStatus.SERVICE_UNAVAILABLE)

        request.session['gs_credentials'] = credentials.google_sheet_credentials
        serializer = GoogleSheetIntegrationSerializer(
            context={'request': request, 'SESSION': SESSION},
            data=SESSION['data'])

        serializer.is_valid(raise_exception=True)
        serializer.save()
        poll_id = SESSION['data']['id']
        # redirect_url = f'https://auditorpro.info/poll/{poll_id}/?closed=true'
        redirect_url = f'{settings.DOMAIN}/api/v1/poll/my/list/'

        return HttpResponseRedirect(redirect_url)
