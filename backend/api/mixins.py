from rest_framework import mixins, viewsets


class UserMixins(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass
