import pyotp
import qrcode


def generate_qr_code(
    provisioning_uri: str = "example@domain.com", issuer_name: str = "MyApp"
):
    # Create a TOTP object with a secret
    totp = pyotp.TOTP(pyotp.random_base32())

    # Get provisioning URI and create a QR code
    uri = totp.provisioning_uri(provisioning_uri, issuer_name=issuer_name)

    img = qrcode.make(uri)
    img.save("qrcode.png")
