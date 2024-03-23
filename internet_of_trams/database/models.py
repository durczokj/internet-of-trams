from tortoise import fields
from tortoise.models import Model
from django.utils import timezone

class Line(Model):
    id = fields.CharField(max_length=50, pk=True)
    name = fields.CharField(max_length=255)
    
class Stop(Model):
    id = fields.CharField(max_length=10, pk=True)
    name = fields.CharField(max_length=255)

class Pole(Model):
    stop = fields.ForeignKeyField("models.Stop", related_name="poles")
    number = fields.IntField(null=True)
    longitude = fields.FloatField()
    latitude = fields.FloatField()

    class Meta:
        unique_together = (("stop", "number"),)
    
class Vehicle(Model):
    id = fields.IntField(pk=True)
    type = fields.CharField(max_length=255)
    line = fields.ForeignKeyField("models.Line", related_name = "vehicles")
    brigade = fields.IntField()

class Appearance(Model):
    vehicle = fields.ForeignKeyField("models.Vehicle", related_name="appearances")
    timestamp = fields.DatetimeField()
    longitude = fields.FloatField()
    latitude = fields.FloatField()

    class Meta:
        unique_together = (("vehicle", "timestamp"),)

class Destination(Model):
    line = fields.ForeignKeyField("models.Line", related_name = "destinations")
    number = fields.IntField()
    stop_id = fields.CharField(max_length=10)
    pole_number = fields.IntField()

    class Meta:
        unique_together = (("line", "number"),)
