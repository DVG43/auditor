import graphene

from poll.schema.queries.poll import QueryPoll
from poll.schema.queries.surveypassing import QuerySurveyPassing
from poll.schema.queries.answers import QueryUserAnswers


class Query(QueryPoll, QuerySurveyPassing, QueryUserAnswers, graphene.ObjectType):
    pass
