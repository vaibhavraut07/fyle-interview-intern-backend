from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.apis.decorators import authenticate_principal, accept_payload
from core.libs import assertions
from core.models.assignments import Assignment, AssignmentStateEnum
from core.apis.schemas import (
    AssignmentDraftSchema,
    AssignmentEditSchema,
    AssignmentSubmitSchema,
    AssignmentSchema
)
from flask import jsonify

from .schema import AssignmentSchema, AssignmentSubmitSchema
student_assignments_resources = Blueprint('student_assignments_resources', __name__)


@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@authenticate_principal
def list_assignments(p):
    """List all assignments for the student."""
    assignments = Assignment.query.filter_by(student_id=p.student_id).all()
    assignments_dump = AssignmentSchema(many=True).dump(assignments)
    return APIResponse.respond(data=assignments_dump)


@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@accept_payload
@authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    assignment = AssignmentSchema().load(incoming_payload)
    assignment.student_id = p.student_id

    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)


@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@accept_payload
@authenticate_principal
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)

    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id,
        auth_principal=p
    )
    db.session.commit()
    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(data=submitted_assignment_dump)

# New endpoint: Create draft assignment
@student_assignments_resources.route('/assignments/draft', methods=['POST'], strict_slashes=False)
@accept_payload
@authenticate_principal
def create_draft_assignment(p, incoming_payload):
    """Create a new draft assignment."""
    draft_payload = AssignmentDraftSchema().load(incoming_payload)
    new_assignment = Assignment(
        student_id=p.student_id,  # Assumes the principal object carries student_id for student users
        content=draft_payload.get('content'),
        state=AssignmentStateEnum.DRAFT
    )
    db.session.add(new_assignment)
    db.session.commit()
    assignment_dump = AssignmentSchema().dump(new_assignment)
    return APIResponse.respond(data=assignment_dump)

# New endpoint: Edit an existing draft assignment
@student_assignments_resources.route('/assignments/draft', methods=['PUT'], strict_slashes=False)
@accept_payload
@authenticate_principal
def edit_draft_assignment(p, incoming_payload):
    """Edit an existing draft assignment."""
    edit_payload = AssignmentEditSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(edit_payload.get('id'))
    assertions.assert_found(assignment, 'Draft assignment not found')
    assertions.assert_valid(
        assignment.state == AssignmentStateEnum.DRAFT,
        'Only draft assignments can be edited'
    )
    assertions.assert_valid(
        assignment.student_id == p.student_id,
        'You can only edit your own assignments'
    )
    # Update assignment content
    assignment.content = edit_payload.get('content')
    db.session.commit()
    assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=assignment_dump)
