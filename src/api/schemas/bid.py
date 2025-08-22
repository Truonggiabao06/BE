from marshmallow import Schema, fields

class PlaceBidRequest(Schema):
    auction_id = fields.Int(required=True)
    item_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    auto_bid = fields.Bool(load_default=False)

class BidResponse(Schema):
    id = fields.Int(required=True)
    auction_id = fields.Int()
    item_id = fields.Int()
    user_id = fields.Int()
    amount = fields.Float()
    created_at = fields.DateTime()
