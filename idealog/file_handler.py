from flask import Blueprint, send_file

bp = Blueprint('file_handler', __name__)

@bp.route('/js/<path:filename>')
def serve_js(filename):
    return send_file(f'js/{filename}')

@bp.route('/prototypes/buildingKB/lib/bindings/<path:filename>')
def serve_bindings_js(filename):
    return send_file(f'prototypes/buildingKB/lib/bindings/{filename}')