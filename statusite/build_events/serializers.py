from rest_framework import serializers

class BuildEventRepositorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    owner = serializers.CharField(max_length=255)

class BuildEventSerializer(serializers.Serializer):
    repo = BuildEventRepositorySerializer()
    tag = serializers.CharField(max_length=255)
    plan_name = serializers.CharField(max_length=255)
    build_id = serializers.IntegerField()
    status = serializers.CharField(max_length=20)
    start_date = serializers.DateField()
    tests_pass = serializers.IntegerField()
    tests_fail = serializers.IntegerField()
    tests_total = serializers.IntegerField()
    build_data = serializers.JSONField()

