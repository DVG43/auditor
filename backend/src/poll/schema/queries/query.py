import graphene

from poll.schema.queries.poll import QueryPoll
from poll.schema.queries.syrveypassing import QuerySurveyPassing


class Query(QueryPoll,QuerySurveyPassing, graphene.ObjectType):
    pass
