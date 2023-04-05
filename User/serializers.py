from rest_framework.serializers import ModelSerializer
from .models import User
from Team.serializers import TeamSerializer


class TinyUserSerializer(ModelSerializer):
    # team = TeamSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            # "team",
        )


class PrivateUserSerializer(ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "team",
        )
