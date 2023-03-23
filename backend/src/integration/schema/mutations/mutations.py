import graphene

from integration.schema.mutations.googlesheet import IntegrationMutation


class Mutation(
    IntegrationMutation,
    graphene.ObjectType
):
    pass
