import asyncio
import aiohttp
import json
import os

from discord.ext import commands
import discord


def _immaculater_url():
    return 'https://%s' % os.environ["IMMACULATER_URL"]


description = f"""A Discord bot for {_immaculater_url()}

Immaculater source code: https://github.com/chandler37/immaculater

This bot's source code: https://github.com/chandler37/immaculater-discord-bot

'!help' shows this message but you really want '!! help' to see help for
Immaculater's command-line interface.

!! help
!! do find a cool job
!! cd /inbox && complete 'find a cool job'
!! rmact uid=37
!! view all_even_deleted && ls -R /
"""


class RoboImmaculater(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or(os.environ.get("DISCORD_COMMAND_PREFIX", "!")),
                         description=description, pm_help=None)

bot = RoboImmaculater()

@bot.command()
async def echo(*args):
    await bot.say(f'You passed in {args}')


@bot.command(name="!")
async def sh(*args):
    tmp = await client.send_message(
        message.channel,
        'Waking %s from sleep... wishing we used Heroku hobby dynos...' % _immaculater_name())
    await client.edit_message(
        tmp,
        await _immaculater_response(user_uid=message.author.id,
                                    commands=' '.join(args)))


@bot.command()
async def open():
    await bot.say(f'{_immaculater_url()}/todo')


async def _immaculater_response(user_uid=None, commands=None):
    assert _immaculater_url().startswith('https://')  # let's keep our secrets
    result = []
    list_of_commands = commands.strip().split('&&') if commands.strip() else ["help"]
    headers = {'Content-type': 'application/json'}
    auth = aiohttp.helpers.BasicAuth(login=str(client.user.id),
                                     password=os.environ["IMMACULATER_BOT_SECRET"])
    async with aiohttp.ClientSession(auth=auth, headers=headers) as session:
        async with session.post(_immaculater_url() + "/todo/discordapi",
                                data=json.dumps({'commands': list_of_commands,
                                                 'discord_user': user_uid,
                                                 'read_only': False})) as r:
            if r.status == 200:
                j = await r.json()
                for x in j['printed']:
                    result.append(x)
            else:
                try:
                    j = await r.json()
                    if isinstance(j, dict) and 'immaculater_error' in j:
                        result.append(j['immaculater_error'])
                    else:
                        result.append(unicode(j))
                except ValueError:
                    text = await r.text()
                    if r.status == 403:
                        if 'FirstLoginRequired' in text:
                            result.append(
                                'Permission denied -- you must first log into %s via Discord'
                                % _immaculater_url())
                        else:
                            result.append('Permission denied')
                    else:
                        result.append('ERROR: Status code %s' % r.status)
                        result.append(text)
    result = '\n'.join(result)
    return result if result else 'okay, remembered!'


def _immaculater_name():
    return os.environ.get("IMMACULATER_DISPLAY_NAME", _immaculater_url())


bot.run(os.environ["DISCORD_TOKEN"])
