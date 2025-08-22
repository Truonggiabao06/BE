from marshmallow import Schema, fields

class LoginRequest(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class RegisterRequest(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=False)

class TokenResponse(Schema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=False)
    token_type = fields.Str(dump_default="Bearer")
