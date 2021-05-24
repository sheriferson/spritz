# Spritz: simple notification of recent precipition near you

![Spritz screenshots](screenshots.jpg)

<small>'Spritz that Shit' is an inside joke. You can make the title whatever you want.</small>

## Setup

```bash
pip install -r requirements.txt
```

You'll need API tokens to [OpenWeatherMap][] and [Pushover][], saved in a `tokens.yml` file:

[OpenWeatherMap]: https://openweathermap.org/price "OpenWeatherMap Pricing page."
[Pushover]: https://pushover.net "Pushover service for notifications."

```yaml
owm_token: ...
pushover_token: '...'
pushover_user_key: '...'
```

Then set your `TIMEZONE` and `LOCATION` variables in `spritz.py`.

## Usage

```bash
python3 spritz.py
```

## Scheduling

I have this running on a Linux host, and I use cron to run the script early morning Pacific time.

```bash
crontab -e
# in the file
0 14 * * * python3 /home/sherif/projects/spritz/spritz.py
```


## ~~todos~~ Nice to change one day

- [ ] Detect user's local timezone automatically.
- [ ] Set location in a different way other than hardcoding a variable inside `spritz.py`.
