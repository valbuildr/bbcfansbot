class BBCFansBot:
    token = ""

class NewsFansHelper:
    token = ""

    class AnnouncementRelay:
        from_server_id = 0
        from_channel_id = 0

        to_webhook_url = ""

class Nitro:
    secret = ""



# dont edit these
# these are only for backwards compatability

main_discord_token = BBCFansBot.token
helper_discord_token = NewsFansHelper.token
nf_announcement_webhook_url = NewsFansHelper.AnnouncementRelay.to_webhook_url
nitro_secret = Nitro.secret
