import graphene

from poll.schema.queries.poll import QueryPoll


class Query(QueryPoll, graphene.ObjectType):
    pass
