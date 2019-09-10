import graphene
from graphene_django import DjangoObjectType
from .models import Track, Like
from  users.schema import UserType
from graphql import GraphQLError

class TrackType(DjangoObjectType):
    class Meta:
        model = Track

class LikeType(DjangoObjectType):
    class Meta:
        model = Like

class Query(graphene.ObjectType):
    tracks = graphene.List(TrackType)
    likes = graphene.List(LikeType)

    def resolve_tracks(self, info):
        return Track.objects.all()

    def resolve_likes(self, info):
        return Like.objects.all()


class CreateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login to create track')
        track = Track.objects.create(title=kwargs.get('title'), description=kwargs.get('description'), url=kwargs.get('url'), posted_by=user)
        #track.save()
        return CreateTrack(track=track)

class UpdateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
        track_id = graphene.Int(required=True)

    def mutate(self, info, **kwargs):
        title = kwargs.get('title')
        description = kwargs.get('description')
        url = kwargs.get('url')
        track_id = kwargs.get('track_id')
        user = info.context.user
        try:
             track = Track.objects.get(id=track_id)
        except:
            raise GraphQLError('Track does not exist')
        if track.posted_by != user:
            raise GraphQLError('Not permitted to update')
        track.title = title
        track.description = description
        track.url = url
        track.save()
        return UpdateTrack(track=track)

class DeleteTrack(graphene.Mutation):
    track_id = graphene.Int()

    class Arguments:
        track_id = graphene.Int()

    def mutate(self, info, track_id):
        user = info.context.user
        try:
            track = Track.objects.get(id=track_id)
        except:
            raise GraphQLError('Track does not exist')
        if track.posted_by != user:
            raise GraphQLError('Not permitted to delete')
        track.delete()
        return DeleteTrack(track_id=track_id)

class LikeTrack(graphene.Mutation):
    user = graphene.Field(UserType)
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info, track_id):
        user = info.context.user
        try:
            track = Track.objects.get(id=track_id)
        except:
            raise GraphQLError('Track does not exist')
        Like(user=user, track=track).save()
        return LikeTrack(user=user, track=track)





class Mutation(graphene.ObjectType):
    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    like_track = LikeTrack.Field()

