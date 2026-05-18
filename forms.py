"""WTForms for validation."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    FloatField,
    IntegerField,
    SelectField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    Regexp,
)


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField(
        "Phone",
        validators=[
            DataRequired(),
            Regexp(r"^[6-9]\d{9}$", message="Enter valid 10-digit Indian mobile number."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Regexp(r"^[6-9]\d{9}$", message="Enter valid 10-digit mobile number."),
        ],
    )
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    city = StringField("City", validators=[Optional(), Length(max=80)])
    pincode = StringField(
        "Pincode",
        validators=[Optional(), Regexp(r"^\d{6}$", message="Enter valid 6-digit pincode.")],
    )
    submit = SubmitField("Update Profile")


class CheckoutForm(FlaskForm):
    shipping_name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    shipping_phone = StringField(
        "Phone",
        validators=[
            DataRequired(),
            Regexp(r"^[6-9]\d{9}$", message="Enter valid 10-digit mobile number."),
        ],
    )
    shipping_address = TextAreaField("Address", validators=[DataRequired(), Length(max=500)])
    shipping_city = StringField("City", validators=[DataRequired(), Length(max=80)])
    shipping_pincode = StringField(
        "Pincode",
        validators=[DataRequired(), Regexp(r"^\d{6}$", message="Enter valid pincode.")],
    )
    payment_method = SelectField(
        "Payment Method",
        choices=[("COD", "Cash on Delivery"), ("UPI", "UPI (Simulated)"), ("Card", "Card (Simulated)")],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Order Notes", validators=[Optional(), Length(max=300)])
    submit = SubmitField("Place Order")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=150)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField("Send Message")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10)])
    price = FloatField("Price (₹)", validators=[DataRequired(), NumberRange(min=1)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("Image URL", validators=[DataRequired(), Length(max=500)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    is_featured = BooleanField("Featured Product")
    is_festival_kit = BooleanField("Festival Pooja Kit")
    submit = SubmitField("Save Product")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save Category")
