# immaculater-discord-bot
Discord bot that talks to Immaculater's django server

Immaculater is https://github.com/chandler37/immaculater

- heroku login
- heroku create <yourapp>
- heroku git:remote -a <yourapp>
- heroku config:set DISCORD_TOKEN=<see https://discordapp.com/developers/applications/me>
- git push heroku master
- heroku scale worker=1
