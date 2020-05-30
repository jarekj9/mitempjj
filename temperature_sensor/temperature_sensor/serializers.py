from rest_framework import serializers

class MitempSerializer(serializers.Serializer):
   """Serialize data for API"""
   date = serializers.DateField()
   temperature = serializers.FloatField()
   humidity = serializers.FloatField()
   battery = serializers.IntegerField()