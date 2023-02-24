import graphene

from document.schema import Query as QueryDocument
from document.schema import Mutation as MutationDocument
from document.schema import Subscription as SubscriptionDocument
from poll.schema.queries.query import Query as QueryPoll
from poll.schema.mutations.mutations import Mutation as MutationPoll
from timing.schema import Query as QueryTiming
from timing.schema import Mutation as MutationTiming
from timing.schema import Subscription as SubscriptionTiming


class Query(QueryDocument, QueryTiming, QueryPoll):
    pass


class Mutation(MutationDocument, MutationTiming, MutationPoll):
    pass


class Subscription(SubscriptionTiming, SubscriptionDocument):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
