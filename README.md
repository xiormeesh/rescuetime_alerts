# rescuetime_alerts

**Deprecated, moving to a telegram bot**

Pulls data from your RescueTime account and pushes desktop notfications (\*nix) according to configured rules.

### Prerequisites

- \*buntu
- a RescueTime account
- python3: matplotlib, pandas

1. Create config.json providing your API token to your RescueTime account:

```
{
	"API_URL": "https://www.rescuetime.com/anapi/data",
	"API_TOKEN": "YOUR_TOKEN",
	"EXPLORE": false,
	"PLOT": false
}
```
2. Create tasks.json with at least one notification according to the following template:
```
{
	"task_type": "limit"|"goal"|"productivity",
	"slice_name": "Entertainment"|"Software Development"|...|,
	"minutes": MIN_NUMBER
}
```
for example:
a notification is sent if more than 60 min have been spent on applications from "Entertainment" category today:
```
{
	"task_type": "limit",
	"slice_name": "Entertainment",
	"minutes": 60
}
```
a notification is sent if more than 180 minutes have been spent on applications from "Software Development" category today:
```
{
	"task_type": "goal",
	"slice_name": "Software Development",
	"minutes": 180
}
```
a notification will be sent specifying your progress towards 300 productive minutes today
```
{
	"task_type": "productivity",
	"minutes": 300
}
```

### Running

You can run the script manually:

```
python3 run.py
```

or set up a cronjob.

On systems with multiple displays you might need to pass DISPLAY var:
```
1 * * * * cd CHECKOUT_PATH/rescuetime_alerts && env DISPLAY=:0 python3 run.py
```

## License

This project is licensed under the GPLv2 License - see the [LICENSE.md](LICENSE.md) file for details
