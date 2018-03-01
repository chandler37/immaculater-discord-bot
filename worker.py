import asyncio
import aiohttp
import json
import os

import discord


client = discord.Client()


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


def _immaculater_url():
    return 'https://%s' % os.environ["IMMACULATER_URL"]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


def _usage_message():
    return '\n'.join(
        [
            "Hello, I am %s, a bot for %s." % (client.user.name, _immaculater_name()),
            "Usage:",
            "",
            "!i help",
            "!i do buy soymilk",
            "!i cd /inbox && complete 'buy soymilk'",
            ])


@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    elif message.content.startswith('!who'):
        await client.send_message(
            message.channel,
            'You are %s#%s with ID %s' %
            (message.author.name, message.author.discriminator, message.author.id))
    # TODO(chandler37): An 'open' command that launches immaculater in a web
    # browser.
    #
    # TODO(chandler37): Help on these commands
    #
    # TODO(chandler37): What do we do if no !command is given?
    elif message.content.startswith('!i '):
        tmp = await client.send_message(
            message.channel,
            'Waking %s from sleep... wishing we used Heroku hobby dynos...' % _immaculater_name())
        await client.edit_message(
            tmp,
            await _immaculater_response(user_uid=message.author.id,
                                        commands=message.content[len('!i '):]))
    elif message.content.startswith('!help'):
        await client.send_message(
            message.channel,
            _usage_message())
    elif len(message.content):
        print('DLC message.content=%s' % message.content)


client.run(os.environ["DISCORD_TOKEN"])
