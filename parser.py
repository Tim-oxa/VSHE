from datetime import datetime
import re


async def get_resources(logs: str, user_id: int):
    pattern = re.compile(
        r"(?P<date>\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2}.\d{6}) from (((tcp)|(udp)):)?(?P<ip>\d+.\d+.\d+.\d+:\d+) accepted ((tcp)|(udp)):(?P<resource>[^:]+):\d+ \[.+\] email: " + str(
            user_id)
    )

    resources = {}

    for line in logs.splitlines():
        match = pattern.match(line)
        if match:
            data = match.groupdict()
            data["date"] = datetime.strptime(match.group("date"), "%Y/%m/%d %H:%M:%S.%f")

            resource = data["resource"]
            resources[resource] = {
                "domain": resource,
                "name": resource.split(".")[-2].capitalize(),
                "date": data["date"].time().strftime("%H:%M:%S"),
            }

    ip_pattern = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    sites = []
    for resource in resources:
        match = ip_pattern.match(resources[resource]["domain"])
        if not match:
            sites.append(resources[resource])

    return sites
