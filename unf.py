from instabot import Bot

bot = Bot(verbosity=True)

bot.login(username = "random.blabber", password = "Istrd@123")

bot.unfollow_non_followers()