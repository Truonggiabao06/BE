from marshmallow import Schema, fields

class CreatePaymentRequest(Schema):
    order_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    method = fields.Str(required=False)

class PaymentResponse(Schema):
    id = fields.Int(required=True)
    order_id = fields.Int()
    amount = fields.Float()
    method = fields.Str()
    status = fields.Str()
    tx_ref = fields.Str(allow_none=True)
