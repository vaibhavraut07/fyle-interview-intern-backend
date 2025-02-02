from flask import Blueprint, request
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.models.teachers import Teacher
from core.models.principals import Principal
from .schema import AssignmentSchema, AssignmentGradeSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """List all assignments submitted and/or graded by teachers under the principal."""
    # Fetch all assignments that are either submitted or graded, no need to check specific teacher assignments
    all_assignments = Assignment.filter(
        Assignment.state.in_(['SUBMITTED', 'GRADED'])
    ).all()

    if not all_assignments:
        return APIResponse.respond(data=[])

    # Serialize assignments
    all_assignments_dump = AssignmentSchema().dump(all_assignments, many=True)

    return APIResponse.respond(data=all_assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def regrade_assignment(p, incoming_payload):
    """Re-grade an assignment that has already been graded by a teacher."""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()

    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)


@principal_assignments_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def fetch_teachers(principal):
    """Retrieve the list of teachers managed by the principal."""
    teacher_list = Teacher.query.all()

    if not teacher_list:
        return APIResponse.respond(data=[])

    teachers_info = [
        {
            "id": teacher.id,
            "user_id": teacher.user_id,
            "created_at": teacher.created_at.isoformat(),
            "updated_at": teacher.updated_at.isoformat()
        }
        for teacher in teacher_list
    ]

    return APIResponse.respond(data=teachers_info)
