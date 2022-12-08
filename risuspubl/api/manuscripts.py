#!/home/kmfahey/Workspace/NuCampFolder/Python/2-SQL/week3/venv/bin/python3

from werkzeug.exceptions import NotFound

from flask import abort, Blueprint, jsonify, request, Response

from risuspubl.api.commons import *
from risuspubl.api.endpfact import update_class_obj_by_id_factory, show_class_obj_by_id, show_class_index
from risuspubl.dbmodels import *


blueprint = Blueprint('manuscripts', __name__, url_prefix='/manuscripts')


manuscripts_indexer = show_class_index(Manuscript)


@blueprint.route('', methods=['GET'])
def index():
    """
    Implements a GET /manuscripts endpoint. All rows in the manuscripts table
    are loaded and output as a JSON list.

    :return:    A flask.Response object.
    """
    return manuscripts_indexer()


manuscript_by_id_shower = show_class_obj_by_id(Manuscript)


@blueprint.route('/<int:manuscript_id>', methods=['GET'])
def show_manuscript_by_id(manuscript_id: int):
    """
    Implements a GET /manuscripts/<id> endpoint. The row in the manuscripts
    table with the given manuscript_id is loaded and output in JSON.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    load and display.
    :return:        A flask.Response object.
    """
    return manuscript_by_id_shower(manuscript_id)


# A Create endpoint is deliberately not implemented, because without
# a way to specify the author or authors to attach the manuscript to, no
# entry in the authors_manuscripts table would be created and the manuscript
# would an orphan in the database. /authors/<author_id>/manuscripts and
# /authors/<author1_id>/<author2_id>/manuscripts already accept Create actions and
# when done that way associations with an author or authors can be created
# appropriately.


manuscript_by_id_updater = update_class_obj_by_id_factory(Manuscript, 'manuscript_id')


@blueprint.route('/<int:manuscript_id>', methods=['PATCH', 'PUT'])
def update_manuscript_by_id(manuscript_id: int):
    """
    Implements a PATCH /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is updated from the JSON parameters.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    update.
    :return:        A flask.Response object.
    """
    return manuscript_by_id_updater(manuscript_id, request.json)


@blueprint.route('/<int:manuscript_id>', methods=['DELETE'])
def delete_manuscript(manuscript_id: int):
    """
    Implements a DELETE /manuscripts/<id> endpoint. The row in the manuscripts
    table with that manuscript_id is deleted.

    :manuscript_id: The manuscript_id of the row in the manuscripts table to
                    delete.
    :return:        A flask.Response object.
    """
    try:
        manuscript_obj = Manuscript.query.get_or_404(manuscript_id)
        # A delete expression for row in the authors_manuscripts table with the
        # given manuscript_id, which need to be deleted as well.
        am_del = Authors_Manuscripts.delete().where(Authors_Manuscripts.columns[1] == manuscript_id)
        db.session.execute(am_del)
        db.session.commit()
        db.session.delete(manuscript_obj)
        db.session.commit()
        return jsonify(True)
    except Exception as exception:
        status = 400 if isinstance(exception, ValueError) else 500
        return (Response(f"{exception.__class__.__name__}: {exception.args[0]}", status=status)
                if len(exception.args) else abort(status))
