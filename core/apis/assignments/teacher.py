from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentGradeSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    # Bug: This API was returning all assignments instead of assignments assigned to the teacher
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    if not teachers_assignments:
        return APIResponse.respond(data=[])
    
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def assign_grade(principal, payload):
    """Assign a grade to an assignment."""
    grade_data = AssignmentGradeSchema().load(payload)

    graded_record = Assignment.mark_grade(
        _id=grade_data.id,
        grade=grade_data.grade,
        auth_principal=principal
    )
    db.session.commit()
    result = AssignmentSchema().dump(graded_record)
    return APIResponse.respond(data=result)
