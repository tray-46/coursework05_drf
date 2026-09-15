from django.db import transaction
from rest_framework import serializers

from habits.models import Action, Location, Reward, Habit
from users.serializers import UserSerializer


class ActionSerializer(serializers.ModelSerializer):
    """
    Serializer for Action model
    """

    class Meta:
        model = Action
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}

    def create(self, validated_data):
        action, _ = Action.objects.get_or_create(**validated_data)
        return action


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for Location model
    """

    class Meta:
        model = Location
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}

    def create(self, validated_data):
        location, _ = Location.objects.get_or_create(**validated_data)
        return location


class RewardSerializer(serializers.ModelSerializer):
    """
    Serializer for Reward model
    """

    class Meta:
        model = Reward
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}

    def create(self, validated_data):
        reward, _ = Reward.objects.get_or_create(**validated_data)
        return reward


class HabitSerializer(serializers.ModelSerializer):
    """
    Serializer for Habit model
    """
    user = UserSerializer(read_only=True)
    action = ActionSerializer()
    location = LocationSerializer()
    reward = RewardSerializer(required=False, allow_null=True)

    class Meta:
        model = Habit
        fields = ("id", "user", "action", "location", "duration", "reminder_time", "period", "related_habit", "reward",
                  "is_pleasant","is_public",)
        extra_kwargs = {
            "related_habit": {
                "error_messages": {
                    "does_not_exist": "Selected choice is invalid or not allowed. Pleas select pleasant habit",
                }
            }
        }

    def create(self, validated_data):
        action_data = validated_data.pop("action")
        action_serializer = ActionSerializer(data=action_data)
        action_serializer.is_valid(raise_exception=True)
        action = action_serializer.save()

        location_data = validated_data.pop("location")
        location_serializer = LocationSerializer(data=location_data)
        location_serializer.is_valid(raise_exception=True)
        location = location_serializer.save()

        reward_data = validated_data.pop("reward")
        reward = None
        if reward_data:
            reward_serializer = RewardSerializer(data=reward_data)
            reward_serializer.is_valid(raise_exception=True)
            reward = reward_serializer.save()

        habit = Habit.objects.create(**validated_data, action=action, location=location, reward=reward)
        return habit

    def update(self, instance, validated_data):
        with transaction.atomic():
            action_data = validated_data.pop("action", None)
            action = None
            if action_data:
                action_serializer = ActionSerializer(data=action_data)
                action_serializer.is_valid(raise_exception=True)
                action = action_serializer.save()

            location_data = validated_data.pop("location", None)
            location = None
            if location_data:
                location_serializer = LocationSerializer(data=location_data)
                location_serializer.is_valid(raise_exception=True)
                location = location_serializer.save()

            reward_data = validated_data.pop("reward", None)
            reward = None
            if reward_data:
                reward_serializer = RewardSerializer(data=reward_data)
                reward_serializer.is_valid(raise_exception=True)
                reward = reward_serializer.save()

            instance.action = action if action else instance.action
            instance.location = location if location else instance.location
            instance.duration = validated_data.get("duration", instance.duration)
            instance.reminder_time = validated_data.get("reminder_time", instance.reminder_time)
            instance.period = validated_data.get("period", instance.period)
            instance.related_habit = validated_data.get("related_habit", instance.related_habit)
            instance.reward = reward if reward else instance.reward
            instance.is_pleasant = validated_data.get("is_pleasant", instance.is_pleasant)
            instance.is_public = validated_data.get("is_public", instance.is_public)
            instance.save()
        return instance



    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.related_habit:
            representation["related_habit"] = self.__class__(instance.related_habit).data

        return representation

    def validate_duration(self, value):
        """Check that the duration value is between 1 and 120"""
        if not 1 <= value <= 120:
            raise serializers.ValidationError("duration must be between 1 and 120 seconds")
        return value

    def validate_period(self, value):
        """Check that the period value is between 1 and 7"""
        if not 1 <= value <= 7:
            raise serializers.ValidationError("period must be between 1 and 7 days")
        return value

    def validate_related_habit(self, value):
        """Check that the related_habit is a pleasant habit"""
        if value and not value.is_pleasant:
            print(value.is_pleasant)
            raise serializers.ValidationError("related_habit must be a pleasant habit")
        return value


    def validate(self, data):
        """Cross field validation"""
        is_pleasant = data.get("is_pleasant")
        related_habit = data.get("related_habit")
        reward = data.get("reward")

        if related_habit is not None and reward is not None:
            raise serializers.ValidationError("habit cannot have both related_habit and reward.")

        if (is_pleasant is not None and is_pleasant == True) and (related_habit is not None or reward is not None):
            raise serializers.ValidationError("pleasant habit cannot have related_habit or reward.")

        if (is_pleasant is not None and is_pleasant == False) and (related_habit is None and reward is None):
            print(f"{is_pleasant=} and {related_habit=} and {reward=}")
            raise serializers.ValidationError("habit must have related_habit or reward.")

        return data

