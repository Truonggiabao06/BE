from marshmallow import Schema, fields

class PaginationSchema(Schema):
    page = fields.Int(dump_default=1)
    limit = fields.Int(dump_default=20)
    total = fields.Int(dump_default=0)

class ErrorSchema(Schema):
    error = fields.Str(required=True)
    details = fields.Dict(required=False)
