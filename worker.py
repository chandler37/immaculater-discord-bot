import asyncio
import aiohttp
import json
import os
import shlex

from discord.ext import commands
import discord


def _immaculater_url():
    return 'https://%s' % os.environ["IMMACULATER_URL"]


def _command_prefix():
    return os.environ.get("DISCORD_COMMAND_PREFIX", "?")


description = f"""A Discord bot for {_immaculater_url()}

Before first using this bot, visit the above site and create an Immaculater
account by signing in with your Discord account.

Immaculater source code: https://github.com/chandler37/immaculater

This bot's source code: https://github.com/chandler37/immaculater-discord-bot

Standalone command-line interface: https://github.com/chandler37/immaculater-cli

In-browser command-line interface: {_immaculater_url()}/todo/cli

'{_command_prefix()}help' shows this message but you really want '{_command_prefix()}{_command_prefix()} help' to see help for
Immaculater's command-line interface.

{_command_prefix()}{_command_prefix()} help
{_command_prefix()}{_command_prefix()} do find a cool job
{_command_prefix()}{_command_prefix()} maybe advance the field of Computer Science
{_command_prefix()}{_command_prefix()} todo
{_command_prefix()}{_command_prefix()} cd /inbox && complete 'find a cool job'
{_command_prefix()}{_command_prefix()} view all_even_deleted && ls -R /
{_command_prefix()}{_command_prefix()} rmact uid=37
"""


class RoboImmaculater(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or(_command_prefix()),
                         description=description, pm_help=None)

bot = RoboImmaculater()

@bot.command(name=_command_prefix(), pass_context=True)
async def sh(ctx, *args):
    tmp = await bot.say(
        'Waking %s from sleep... wishing we used Heroku hobby dynos...'
        % _immaculater_name())
    iresponse = await _immaculater_response(
        user_uid=ctx.message.author.id,
        commands=' '.join(shlex.quote(a) for a in args))
    backticks = "```"
    while backticks in iresponse:
        iresponse = iresponse.replace("```", "`\\`")
    await bot.edit_message(
        tmp,
        f'```\n{iresponse}```')


@bot.command()
async def open():
    await bot.say(f'{_immaculater_url()}/todo')


@bot.command(pass_context=True)
async def perms(ctx):
    msg = await bot.say(f'{_immaculater_url()}/todo')
    perm = msg.channel.permissions_for(msg.author)
    await bot.say(f'{perm.value}')


async def _immaculater_response(user_uid=None, commands=None):
    assert _immaculater_url().startswith('https://')  # let's keep our secrets
    result = []
    list_of_commands = commands.strip().split('&&') if commands.strip() else ["help"]
    headers = {'Content-type': 'application/json'}
    auth = aiohttp.helpers.BasicAuth(login=str(bot.user.id),
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
