import graphene

from document.schema import Query as QueryDocument
from document.schema import Mutation as MutationDocument
from document.schema import Subscription as SubscriptionDocument
from timing.schema import Query as QueryTiming
from timing.schema import Mutation as MutationTiming
from timing.schema import Subscription as SubscriptionTiming


class Query(QueryDocument, QueryTiming):
    pass


class Mutation(MutationDocument, MutationTiming):
    pass


class Subscription(SubscriptionTiming, SubscriptionDocument):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
