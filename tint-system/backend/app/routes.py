from flask import Blueprint, jsonify, request
from app.models import Formulation, ColorantDetail
from app import db

formulations_bp = Blueprint('formulations', __name__, url_prefix='/api/formulations')

@formulations_bp.route('/', methods=['GET'])
def get_formulations():
    formulations = Formulation.query.all()
    return jsonify([formulation.to_dict() for formulation in formulations])

@formulations_bp.route('/<color_code>', methods=['GET'])
def get_formulation(color_code):
    formulation = Formulation.query.filter_by(color_code=color_code).first_or_404()
    return jsonify(formulation.to_dict())

@formulations_bp.route('/', methods=['POST'])
def create_formulation():
    data = request.get_json()
    
    # Extract formulation data
    colorants = data.pop('colorants', [])
    
    formulation = Formulation(**data)
    db.session.add(formulation)
    db.session.flush()  # Get the ID before commit
    
    # Add colorant details
    for colorant in colorants:
        colorant_detail = ColorantDetail(
            formulation_id=formulation.id,
            colorant_name=colorant['colorant_name'],
            weight_g=colorant.get('weight_g'),
            volume_ml=colorant.get('volume_ml')
        )
        db.session.add(colorant_detail)
    
    db.session.commit()
    return jsonify(formulation.to_dict()), 201
