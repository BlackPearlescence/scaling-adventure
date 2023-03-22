from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'
    serialize_rules = ('-sweets.vendors', '-vendor_sweets.vendor',"-sweets.vendor")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    vendor_sweets = db.relationship('VendorSweet', backref='vendor')
    sweets = association_proxy('vendor_sweets', 'vendor', creator=lambda s: VendorSweet(sweet=s))

class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'
    serialize_rules = ('-vendors.sweets', '-vendor_sweets.sweet')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    vendor_sweets = db.relationship('VendorSweet', backref='sweet')
    vendors = association_proxy('vendor_sweets', 'sweet', creator=lambda v: VendorSweet(vendor=v))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'
    serialize_rules = ('-sweet.vendor_sweets', '-vendor.vendor_sweets')

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    sweet_id = db.Column(db.Integer, db.ForeignKey('sweets.id'))

    def to_dict(self):
        vendor_sweet = Sweet.query.filter(self.sweet_id == Sweet.id).first()
        return {
            "id": self.id,
            "name": vendor_sweet.name,
            "price": self.price,
        }
    
    @validates("price")
    def price_validation(self,key,price):
        if price == "" or None:
            raise ValueError("Price cannot be blank")
        elif price < 0:
            raise ValueError("Price cannot be a negative number")
    

