from marshmallow import Schema, EXCLUDE, fields, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_enum import EnumField
from core.models.assignments import Assignment, GradeEnum
from core.libs.helpers import GeneralObject  # Assuming GeneralObject is a helper for wrapping data

class AssignmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Assignment
        unknown = EXCLUDE
        load_instance = True  # Automatically load an Assignment instance

    id = auto_field(required=False, allow_none=True)
    content = auto_field()
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    teacher_id = auto_field(dump_only=True)
    student_id = auto_field(dump_only=True)
    grade = auto_field(dump_only=True)
    state = auto_field(dump_only=True)

    @post_load
    def initiate_class(self, data_dict, **kwargs):
        # Returns an Assignment instance when loading data
        return Assignment(**data_dict)


# Schema for creating a draft assignment (only content needed)
class AssignmentDraftSchema(Schema):
    content = fields.String(required=True)

    @post_load
    def create_draft_obj(self, data, **kwargs):
        return data


# Schema for editing an existing draft (id and new content required)
class AssignmentEditSchema(Schema):
    id = fields.Int(required=True)
    content = fields.String(required=True)

    @post_load
    def create_edit_obj(self, data, **kwargs):
        return data


# Schema for assignment submission (id and teacher_id required)
class AssignmentSubmitSchema(Schema):
    id = fields.Int(required=True)
    teacher_id = fields.Int(required=True)

    @post_load
    def create_submit_obj(self, data, **kwargs):
        return data


class AssignmentGradeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Integer(required=True, allow_none=False)
    grade = EnumField(GradeEnum, required=True, allow_none=False)

    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return GeneralObject(**data_dict)
