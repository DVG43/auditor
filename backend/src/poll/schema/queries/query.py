import graphene

from poll.schema.queries.poll import QueryPoll
from poll.schema.queries.surveypassing import QuerySurveyPassing


class Query(QueryPoll, QuerySurveyPassing, graphene.ObjectType):
    pass
