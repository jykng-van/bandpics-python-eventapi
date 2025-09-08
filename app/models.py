from pydantic import BaseModel, Field, ConfigDict, model_validator, field_serializer, AfterValidator, PlainSerializer, WithJsonSchema
from datetime import datetime, timezone, date
from typing import Optional, Any, Union
from typing_extensions import Annotated
from bson import ObjectId


# Validator for object id
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")
# Custom type for MongoDB ObjectId
PyObjectId = Annotated[
    Union[str, ObjectId, Field(default=None)],
    AfterValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]

# MongoDBModel is a base model for MongoDB documents, allowing ids to be of type ObjectId
class MongoDBModel(BaseModel):
    created_at: Optional[datetime] = Field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda:datetime.now(timezone.utc))

    model_config = ConfigDict(
        arbitrary_types_allowed = True,
        populate_by_name=True,
    )

    @field_serializer("id", when_used="json", check_fields=False) # Serializer for id field when used in JSON
    def object_id_to_str(self, v: PyObjectId) -> str:
        return str(v) if v else None

# The
class LiveEvent(MongoDBModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str = Field(description="Event name", default=None)

    description: Optional[str] = Field(default=None, description="Description of the event")
    event_date: Optional[date] = Field(default=None, description="Date of the event")

    location: dict = Field(description="Embedded external data about the event's location", default=None)
    data: dict = Field(description="Embedded external data about the event", default=None)

    @field_serializer('eventDate', when_used='json', check_fields=False)
    def serialize_date(self, d: date, _info):
        return d.strftime('%Y-%m-%d') if d else None

class UpdateLiveEvent(BaseModel): # update model for image data because of group id
    name: Optional[str] = Field(default=None, description="Event name")
    description: Optional[str] = Field(default=None, description="Description of the event")

    event_date: Optional[str] = Field(default=None, description="Date of the event")

    location: dict = Field(description="Embedded external data about the event's location", default=None)

    data: dict = Field(description="Embedded external data about the event", default=None)













