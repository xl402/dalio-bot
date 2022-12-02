from chai_py import Metadata, package, upload_and_deploy, wait_for_deployment
from chai_py import share_bot
from chai_py.auth import set_auth

from production import Bot

DEVELOPER_UID = "nBhoZmdemBNStCU16fc9VcO4BGY2"
DEVELOPER_KEY = "_gwkabJwJfjM5RhRjmoiyNUp5R32T8qW5-JqA7efqGjqbrnrtbL0GtT2aL6AvDT4C51fee5wa-hANOm4X_-jAw"

if DEVELOPER_KEY is None or DEVELOPER_UID is None:
    raise RuntimeError("Please fetch your UID and KEY from the bottom of the Chai Developer Platform. https://chai.ml/dev")

set_auth(DEVELOPER_UID, DEVELOPER_KEY)
BOT_IMAGE_URL = "https://imgur.com/9CLmvI5.png"

package(
    Metadata(
        name="[Team Chai] Ray Dalio v3.2.0 ✅",
        image_url=BOT_IMAGE_URL,
        color="f1a2b3",
        description="Founder of Bridge Water, philanthropist, author of Principles",
        input_class=Bot,
     ),
)

bot_uid = upload_and_deploy(
    "_package.zip"
)

wait_for_deployment(bot_uid)

share_bot(bot_uid)
