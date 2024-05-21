import sys
import os
from twocaptcha import TwoCaptcha


def captcha_resolver():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    api_key = os.getenv('APIKEY_2CAPTCHA', 'f455ea662443a85c9641e40e47522c2c')

    solver = TwoCaptcha(api_key)

    try:
        result = solver.normal("./captcha/captcha.png")

    except Exception as e:
        sys.exit(e)
    else:
        return result
