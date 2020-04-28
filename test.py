
import pyotp
totp = pyotp.TOTP("W7QWUUMIMUTMKUF6")
print("Current OTP:", totp.now())