#!/usr/bin/env python3

from flask import Flask, make_response, jsonify,request
from flask_migrate import Migrate

from models import db, Vendor, VendorSweet, Sweet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/vendors')
def vendors():
    vendors = []

    for vendor in Vendor.query.all():
        vendors.append({
            "id":vendor.id,
            "name": vendor.name,
        })
    
    return make_response(jsonify(vendors),200)

@app.route('/vendors/<int:id>')
def vendor_by_id(id):
    vendor = Vendor.query.filter(Vendor.id == id).first()
    if vendor == None:
        return make_response(jsonify({"error":"Vendor not found"}),404)
    vendor = {
        "id": vendor.id,
        "name": vendor.name,
        "vendor_sweets": [vendor_sweet.to_dict() for vendor_sweet in VendorSweet.query.filter(VendorSweet.vendor_id == vendor.id)]
    }
    return make_response(jsonify(vendor), 200)

@app.route('/sweets')
def sweets():
    sweets = []
    for sweet in Sweet.query.all():
        sweets.append(sweet.to_dict())
    
    return make_response(jsonify(sweets),200)

@app.route('/sweets/<int:id>')
def sweet_by_id(id):
    sweet = Sweet.query.filter(Sweet.id == id).first()
    if sweet == None:
        return make_response(jsonify({"error":"Sweet not found"}),404)
    sweet = sweet.to_dict()
    return make_response(jsonify(sweet),200)

@app.route('/vendor_sweets', methods = ["POST"])
def vendor_sweets():
    if request.method == "POST":
        new_vendor_sweet = VendorSweet(
            price=request.json["price"],
            vendor_id=request.json["vendor_id"],
            sweet_id=request.json["sweet_id"],
        )
        validation_errors = []
        if new_vendor_sweet.vendor_id not in [vendor.id for vendor in Vendor.query.all()]:
            validation_errors.append("Vendor does not exist")
        if new_vendor_sweet.sweet_id not in [sweet.id for sweet in Sweet.query.all()]:
            validation_errors.append("Sweet does not exist")
        if len(validation_errors) == 0:
            db.session.add(new_vendor_sweet)
            db.session.commit()
            return make_response(jsonify(new_vendor_sweet.to_dict()),200)
        else:
            return make_response(jsonify({"errors":validation_errors}),403)

        
@app.route('/vendor_sweets/<int:id>', methods =["DELETE"])
def vendor_sweet_by_id(id):
    if request.method == "DELETE":
        vendor_sweet = VendorSweet.query.filter(VendorSweet.id == id).first()
        if vendor_sweet == None:
            return make_response(jsonify({"error":"VendorSweet not found"}),404)
        db.session.delete(vendor_sweet)
        db.session.commit()
        return make_response(jsonify({}),200)
    



if __name__ == '__main__':
    app.run(port=5555)
