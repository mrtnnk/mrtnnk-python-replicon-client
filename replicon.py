from datetime import datetime, timedelta
start_time = datetime.now()

from dateutil import relativedelta
from libs.replicon_client import RepliconClient
from libs.db_adapter import TimesheetBilling
from libs.project import Project
from libs.user import User

import os
import threading

START_DATE = datetime.now() - relativedelta.relativedelta(months=6)
END_DATE = datetime.now() + relativedelta.relativedelta(months=5)
PER_PAGE = 20

RepliconClient().prepare()
threads = []
downloaded_billings = []

def worker(timesheets):
  # Get Timesheet Billings
  timesheetUris = []
  for value in timesheets.values():
    timesheetUris.append(value['uri'])

  data = {
    "timesheetUris": timesheetUris
  }

  parsed = RepliconClient.query('TimesheetService1', 'BulkGetTimesheetDetails', data)

  for result in parsed['d']:
    timesheet = result['uri']
    slug = result['slug']
    print("Timesheet: {} {}".format(timesheet, slug))
    date_range = result['dateRange']
    start_date = datetime(
      int(date_range['startDate']['year']),
      int(date_range['startDate']['month']),
      int(date_range['startDate']['day'])
    )
    end_date = datetime(
      int(date_range['endDate']['year']),
      int(date_range['endDate']['month']),
      int(date_range['endDate']['day'])
    )
    # puts "StartDate: #{start_date} EndDate: #{end_date}"
    billings = []
    for ta in result['timeAllocations']:
      uri = ta['uri']
      if not ta['project']: #time off
        continue
      duration = float(ta['duration']['hours']) + float(ta['duration']['minutes']) / 60
      date = datetime(int(ta['date']['year']), int(ta['date']['month']), int(ta['date']['day']))
      user_slug = ta['user']['slug']
      hourly_rate = timesheets[slug]['HourlyRate'] if ta['billingRate'] else 0
      project_uri = ta['project']['uri']
      project_slug = ta['project']['slug']
      user_uri = ta['user']['uri']

      billings.append({
        'Entrydate': date,
        'Staffingweek': date - timedelta(days=date.weekday()),
        'Billhours': duration,
        'HourlyRate': hourly_rate,
        'Startdate': start_date,
        'Enddate': end_date,
        'Projectname': Project().name(project_uri),
        'Projectcode': Project().code(project_uri),
        'email': User().email(user_uri),
        'Title': User().title(user_uri),
        'TimesheetSlug': slug[1:1000], #slug without dot
        'ProjectSlug': project_slug,
        'UserSlug': user_slug,
      })

    # billings = sorted(
    #   billings,
    #   key=lambda billing: "{}{}{}".format(
    #     billing['Projectcode'],
    #     billing['email'],
    #     billing['Entrydate'].strftime('%Y-%m-%d')
    #   )
    # )
    downloaded_billings.extend(billings)

# Downloading Timesheet paginated list, then loading
for page in range(1, 10000):
  print(
    "TimesheetList page: {} ({}..{}) Records: {} time: {}".format(
      page,
      (page - 1) * PER_PAGE + 1,
      page * PER_PAGE,
      TimesheetBilling().length(),
      (datetime.now() - start_time).seconds
    )
  )

  data = {
    "page": page,
    "pagesize": PER_PAGE,
    "columnUris": [
        "urn:replicon:timesheet-list-column:timesheet",
        "urn:replicon:timesheet-list-column:billable-amount",
        "urn:replicon:timesheet-list-column:billable-time-duration"
    ],
    "sort": [{
      "columnUri": "urn:replicon:timesheet-list-column:timesheet-period",
      "isAscending": "true"
    }],
    "filterExpression": {
      "leftExpression": {
        "filterDefinitionUri":  "urn:replicon:timesheet-list-filter:timesheet-period-date-range"
      },
      "operatorUri":  "urn:replicon:filter-operator:in",
      "rightExpression": {
        "value": {
          "dateRange": {
            "startDate": {
              "year": START_DATE.year,
              "month": START_DATE.month,
              "day": START_DATE.day
            },
            "endDate": {
              "year": END_DATE.year,
              "month": END_DATE.month,
              "day": END_DATE.day
            }
          }
        }
      }
    }
  }

  parsed = RepliconClient().query('TimesheetListService1', 'GetData', data)
  result = parsed['d']['rows']
  timesheets = {}
  for row in result:
    timesheets[row['cells'][0]['slug']] = {
      "uri": row['cells'][0]['uri'],
      "HourlyRate":
        float(row['cells'][1]['numberValue']) / (float(row['cells'][2]['textValue']) if float(row['cells'][2]['textValue']) != 0.00 else 1.00)
    }

  # fp = open('test/test{}'.format(page), 'w')
  # for key in timesheets:
  #   fp.write('{} -> {} -> {}\n'.format(key, timesheets[key]['uri'], timesheets[key]['HourlyRate']))

  thread = threading.Thread(
    target=worker,
    args=(timesheets,)
  )
  thread.start()
  threads.append(thread)
  if len(timesheets) < PER_PAGE:
    break
for thread in threads:
  thread.join()

# _fp = open('test/python-billing', 'w')

while downloaded_billings:
  billings = downloaded_billings.pop()
  # _fp.write("{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}---{}\n".format(
  #   billings['Entrydate'].strftime('%Y-%m-%d'),
  #   billings['Staffingweek'].strftime('%Y-%m-%d'),
  #   billings['Billhours'],
  #   billings['HourlyRate'],
  #   billings['Startdate'].strftime('%Y-%m-%d'),
  #   billings['Enddate'].strftime('%Y-%m-%d'),
  #   billings['Projectname'],
  #   billings['Projectcode'],
  #   billings['email'],
  #   billings['Title'],
  #   billings['TimesheetSlug'],
  #   billings['ProjectSlug'],
  #   billings['UserSlug']
  # ))
  print("Saving after threads {}".format(len(downloaded_billings)))
  timesheetbilling = TimesheetBilling(
    **billings
  )

  # print('timesheetbilling.hourlyrate = ', timesheetbilling.hourly_rate())
  TimesheetBilling().insert(timesheetbilling)

print("Success! Total time: {}".format((datetime.now()-start_time).seconds))
print("Downloaded records: {}".format(TimesheetBilling().length()))