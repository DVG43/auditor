import graphene

from integration.schema.queries.googlesheet import QueryGoogleSheet


class Query(QueryGoogleSheet, graphene.ObjectType):
    pass
