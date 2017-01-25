#!/usr/bin/env python3
"""Parse quota ouput and print it readable."""

import subprocess
import re


quota_command = ['repquota', '-ua']
user_blacklist = []
base = 1024  # whether SI or Microsoft base should be used
block_size = 1024
base_string = '{:30s}: {: >10s}{: >3s}/{: >10s}{: >3s} ({:5f}%)'


def parse():
    """Parse the output of command."""
    output = str(subprocess.check_output(quota_command))
    lines = output.split(r'\n')

    pattern = (r'(?P<username>\w+)[ ]*--[ ]*(?P<used>\d+)[ ]+' +
               r'(?P<limit_soft>\d+)[ ]+(?P<limit_hard>\d+)')
    pattern = re.compile(pattern)

    all_users = []
    for line in lines:
        match = pattern.search(line)
        if not match:
            continue
        data = match.groupdict()
        if data['username'] in user_blacklist:
            continue
        all_users.append(data)

    return all_users


def human_readable(size):
    """Generate the human readable amount and entity."""
    entity = 'B'

    if size >= base ** 5:
        entity = 'PB'
        size /= base ** 5
    elif size >= base ** 4:
        entity = 'TB'
        size /= base ** 4
    elif size >= base ** 3:
        entity = 'GB'
        size /= base ** 3
    elif size >= base ** 2:
        entity = 'MB'
        size /= base ** 2
    elif size >= base:
        entity = 'KB'
        size /= base

    return size, entity


def format(users):
    """Format the quota data of all users."""
    for user in users:
        used = int(user['used'])
        total = int(user['limit_hard'])
        if total != 0:
            percentage = used / total
        else:
            percentage = 0

        # generate human readable sizes
        used, used_entity = human_readable(used * block_size)
        total, total_entity = human_readable(total * block_size)

        print(base_string.format(user['username'],
              '{:.2f}'.format(used), used_entity,
              '{:.2f}'.format(total), total_entity, percentage))


if __name__ == '__main__':
    format(parse())
