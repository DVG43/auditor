import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from projects.models import Project
from folders.models import Folder
from poll.models import (
    poll as poll_models,
)
from poll.schema import types
from poll.serializers import (
    poll as poll_serializers
)


class CreatePoll(SerializerMutation):
    class Meta:
        serializer_class = poll_serializers.PollSerializer
        model_operations = ['create', 'update']
        lookup_field = 'poll_id'
        model_class = poll_models.Poll

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        prj_id = input["host_project"]
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, prj_id)

        host_project = Project.objects.filter(pk=prj_id).first()
        if "folder" in input:
            folder = Folder.objects.filter(pk=input["folder"]).first()
        else:
            folder = None
        input.update({'owner': info.context.user,
                      'last_modified_user': info.context.user.email,
                      'host_project': host_project,
                      'folder': folder})

        poll = poll_serializers.PollSerializer.create(
            poll_serializers.PollSerializer(),
            validated_data=input
        )

        return poll


class CreatePollTagInput(graphene.InputObjectType):
    name = graphene.String(required=False)


class CreatePollTag(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        polls = graphene.List(graphene.Int)
        tags = graphene.List(CreatePollTagInput)
        prj_id = graphene.ID()

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, polls, tags, prj_id):
        prj_id = prj_id
        PermissionClass.has_permission(root)
        PermissionClass.has_mutate_object_permission(root, prj_id)

        try:
            for poll in polls:
                get_poll = poll_models.Poll.objects.get(poll_id=poll)
                for tag in tags:
                    serialized_tag = poll_serializers.PollTagsSerializer(tag)

                    if not serialized_tag.data['name'] in str(get_poll.tags_list.values_list('name')):
                        get_poll.tags_list.get_or_create(name=tag['name'])
        except Exception as ex:
            return {'error': f'{ex}'}
        return CreatePollTag(ok=True)


class Mutation(graphene.ObjectType):
    create_poll = CreatePoll.Field()
    create_poll_tag = CreatePollTag.Field()
