# Author: Caspar Clemens Mierau <ccm@screenage.de>
# Homepage: https://github.com/leitmedium/weechat-pushover
# Derived from: notifo
#   Author: ochameau <poirot.alex AT gmail DOT com>
#   Homepage: https://github.com/ochameau/weechat-notifo
# And from: notify
#   Author: lavaramano <lavaramano AT gmail DOT com>
#   Improved by: BaSh - <bash.lnx AT gmail DOT com>
#   Ported to Weechat 0.3.0 by: Sharn - <sharntehnub AT gmail DOT com)
# And from: notifo_notify
#   Author: SAEKI Yoshiyasu <laclef_yoshiyasu@yahoo.co.jp>
#   Homepage: http://bitbucket.org/laclefyoshi/weechat/
#
# This plugin sends push notifications to your iPhone or Android smartphone
# by using pushover.net. In order to use it, please follow these steps:
#
# 1. Register an account at http://pushover.net
# 2. Create a new application at https://pushover.net/apps/build
# 3. Note the "token" for your new application (referenced as TOKEN later on)
# 4. From the Dashboard at https://pushover.net note your "User key" (referenced as USERKEY later on)
# 5. Install the pushover app on your iPhone/Android and login
# 6. put "pushover.py" to ~/.weechat/python
# 7. start the plugin with "/python load pushover.py"
# 8. Set user key and token by doing
# 9. /set plugins.var.python.pushover.user USERKEY
# 10. /set plugins.var.python.pushover.token TOKEN
#
# On security: This plugin does not use end-to-end-encryption. Please see
# the security related FAQ at pushover.net for details
#
# Requires Weechat 0.3.0
# Released under GNU GPL v2, see LICENSE file for details
#
# 2012-10-26, au <poirot.alex@gmail.com>:
#     version 0.1: merge notify.py and notifo_notify.py in order to avoid
#                  sending notifications when channel or private buffer is
#                  already opened
# 2013-06-27, au <ccm@screenage.de>:
#     version 0.2: replace blocking curl call
# 2020-09-02, au <ccm@screenage.de>:
#     version 0.3: update to python3 (replace urllib2 with new urllib)
#                  fix minor code glitches with python 3
import weechat, string, os, http.client, urllib


weechat.register(
    'pushover',
    'Caspar Clemens Mierau <ccm@screenage.de>',
    '0.3',
    'GPL',
    (
        'pushover: Send push notifications to you iPhone/Android'
        'about your private message and hilights.'
    ),
    '',
    ''
)

settings = {
    'user': '',
    'token': '',
}

for option, default_value in list(settings.items()):
    if not weechat.config_get_plugin(option):
        weechat.prnt('', f'{weechat.prefix("error")}pushover: Please set option: {option}')
        weechat.prnt('', f'pushover: /set plugins.var.python.pushover.{option} STRING')


# Hook privmsg/hilights
weechat.hook_print('', '','', 1, 'print_hook', '')


# Functions
def print_hook(data, bufferp, uber_empty, tagsn, isdisplayed, ishilight, prefix, message):
    # Get local nick for buffer
    mynick = weechat.buffer_get_string(bufferp, 'localvar_nick')

    # Only notify if the private message was not sent by myself
    if weechat.buffer_get_string(bufferp, 'localvar_type') == 'private' and prefix != mynick:
        send_notification(prefix, prefix, message)

    elif ishilight:
        buffer = weechat.buffer_get_string(bufferp, 'short_name')
        if not buffer:
            buffer = weechat.buffer_get_string(bufferp, 'name')

        send_notification(buffer, prefix, message)

    return weechat.WEECHAT_RC_OK


def send_notification(buffer, nick, message):
    if not any_server_is_away():
        return

    PUSHOVER_USER = weechat.config_get_plugin('user')
    PUSHOVER_API_SECRET = weechat.config_get_plugin('token')

    if not PUSHOVER_USER or not PUSHOVER_API_SECRET:
        return

    conn = http.client.HTTPSConnection('api.pushover.net:443')
    conn.request(
        'POST',
        '/1/messages.json',
        urllib.parse.urlencode({
            'token': PUSHOVER_API_SECRET,
            'user': PUSHOVER_USER,
            'title': f'weechat: {buffer}',
            'message': f'<{nick}> {message}',
        }),
        {'Content-Type': 'application/x-www-form-urlencoded'}
    )


def any_server_is_away():
    infolist = weechat.infolist_get('irc_server', '', '')

    while weechat.infolist_next(infolist):
        if weechat.infolist_integer(infolist, 'is_connected') != 1:
            continue

        if weechat.infolist_integer(infolist, 'is_away'):
            return True

    return False
