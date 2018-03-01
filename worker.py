import asyncio
import aiohttp
import os

import discord


client = discord.Client()


async def _immaculater_response(user_uid=None, commands=None):
    result = []
    def append_result(y):
        result.append(y)
    assert _immaculater_url().startswith('https://')  # let's keep our secrets
    list_of_commands = commands.strip().split('&&') if commands.strip() else ["help"]
    headers = {'Content-type': 'application/json'}
    auth = aiohttp.helpers.BasicAuth(login=str(client.user.id),
                                     password=os.environ["IMMACULATER_BOT_SECRET"])
    async with aiohttp.ClientSession(auth=auth, headers=headers) as session:
        async with session.post(_immaculater_url() + "/todo/discordapi",
                                json={'commands': list_of_commands,
                                      'discord_user': user_uid,
                                      'read_only': False}) as r:
            if r.status == 200:
                for x in r.json()['printed']:
                    append_result(x)
            else:
                try:
                    j = r.json()
                    if isinstance(j, dict) and 'immaculater_error' in j:
                        append_result(j['immaculater_error'])
                    else:
                        append_result(unicode(r.json()))
                except ValueError:
                    text = await r.text()
                    if r.status == 403:
                        if 'FirstLoginRequired' in text:
                            append_result(
                                'Permission denied -- you must first log into %s via Discord'
                                % _immaculater_url())
                        else:
                            append_result('Permission denied')
                    else:
                        append_result('ERROR: Status code %s' % r.status)
                        append_result(text)
    result = '\n'.join(result)
    return result if result else '(okay)'


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


client.run(os.environ["DISCORD_TOKEN"])
