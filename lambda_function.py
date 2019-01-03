import json
import os
import urllib.request, urllib.parse

# Webhooks Document
# https://help.statuspage.io/knowledge_base/topics/webhook-notifications

def messageColor(indicator):
    if indicator == 'major':
        return 'danger'
    elif indicator == 'critical':
        return 'warning'
    elif indicator == 'none':
        return 'good'
    else:
        return 'warning'

def pretext(page):
    indicator = page['status_indicator']
    description = page['status_description']

    if indicator == 'none':
      return description

    return f'`{indicator}` {description}'

def componentFields(component):
    status = component['status']
    name = component['name']
    description = component['description']

    fields = []
    fields.append({ "title": "component", "value": name, "short": True })
    fields.append({ "title": "status", "value": status, "short": True })
    fields.append({ "title": "description", "value": description, "short": False })
    return fields

def componentUpdateFields(component_update):
    old_status = component_update['old_status']
    new_status = component_update['new_status']
    return [{ "title": "update", "value": f'{old_status} → {new_status}', "short": False }]

def makeMessage(page, component, component_update):
    indicator = page['status_indicator']

    fields = []
    fields.extend(componentUpdateFields(component_update))
    fields.extend(componentFields(component))

    attachment = {
        "pretext": pretext(page),
        "color": messageColor(indicator),
        "fields": fields
    }
    body = {
      "username": f'GitHub Status | {indicator}',
      "attachments": [attachment]
    }
    return body

def postMessage(message):
    json_data = json.dumps(message).encode("utf-8")
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    request = urllib.request.Request(webhook_url, data=json_data, method="POST")

    with urllib.request.urlopen(request) as res:
       data = res.read().decode("utf-8")
       print(data)

def lambda_handler(event, context):
    try:
        print(event)
        message = makeMessage(event['page'], event['component'], event['component_update'])
        postMessage(message)
    except Exception as e:
        print(e)
        print(e.message)
        print(event)
