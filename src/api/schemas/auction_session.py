from marshmallow import Schema, fields

class AuctionSessionCreate(Schema):
    title = fields.Str(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    reserve_price = fields.Float(allow_none=True)
    description = fields.Str(allow_none=True)

class AuctionSessionUpdate(Schema):
    title = fields.Str()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    reserve_price = fields.Float(allow_none=True)
    description = fields.Str(allow_none=True)
    status = fields.Str()

class AuctionSessionResponse(Schema):
    id = fields.Int(required=True)
    title = fields.Str()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    reserve_price = fields.Float(allow_none=True)
    description = fields.Str(allow_none=True)
    status = fields.Str()
