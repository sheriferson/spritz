"""
Get historical weather data for Seattle to know if plants need watering
"""
from datetime import datetime, timedelta
import os
from pytz import timezone
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import yaml

from notification import send_message

plt.rcParams["font.family"] = "Helvetica"  # this gets swapped for nearest font on Ubuntu

tokens = yaml.safe_load(open('tokens.yml'))
LOCATION = (47.588993, -122.306286)  # [TODO] Set location in a nicer way.
TIMEZONE = 'US/Pacific'  # [TODO] Find a reliable way of detecting machine's timezone


def unix_to_dt(unixepoch: int, to_local=True) -> datetime:
    """
    Small helper function to parse unix timestamp
    """
    utc_dt = datetime.fromtimestamp(unixepoch)
    if to_local:
        return utc_dt.astimezone(timezone(TIMEZONE))
    else:
        return utc_dt


def get_rain_hours(dayweather: dict) -> list:
    """
    Parse returned weather from OpenWeatherMap API and return list of hours with rain.
    """
    assert 'hourly' in dayweather, "Dict has to contain an 'hourly' key for hourly data."
    hourly = dayweather['hourly']
    rain = [{unix_to_dt(int(hour['dt'])): hour['rain']} for hour in hourly if 'rain' in hour]
    return rain


def total_rain(rain_hours: list) -> int:
    """
    Sum up the rain mm from list of rain hours
    """
    if len(rain_hours) > 0:
        return round(sum([list(x.values())[0]['1h'] for x in rain_hours]), 2)
    else:
        return 0


def get_weather_for_date(inputdate: datetime) -> dict:
    """
    Call OpenWeatherMap history API and return weather dict.
    """
    hist = "http://api.openweathermap.org/data/2.5/onecall/timemachine" \
           f"?lat={LOCATION[0]}&lon={LOCATION[1]}&dt={int(inputdate.timestamp())}&appid={tokens['owm_token']}"
    return requests.get(hist).json()


def save_plot_for_rain(today_date: datetime, filtered_rain_hours: list, img_path: str):
    """
    Save bar plot of rain to attach to notification.
    """
    dates = [today_date - timedelta(days=ii) for ii in [4, 3, 2, 1]]
    historical_rain = []

    for rainday in dates:
        sel_hours = [x for x in filtered_rain_hours if list(x.keys())[0].date() == rainday.date()]
        historical_rain.append(total_rain(sel_hours))

    xloc = mdates.DayLocator()
    xfmt = mdates.DateFormatter('%b %-d')
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(xloc)
    ax.xaxis.set_minor_locator(plt.NullLocator())
    fig = sns.barplot(x=dates, y=historical_rain, palette='pastel', ci=None)
    ax.set_xticklabels([date.strftime('%b %-d') for date in dates])
    max_y = 5 if max(historical_rain) < 5 else max(historical_rain) + 2
    ax.set_ylim([0, max_y])

    for ii in range(len(dates)):
        if historical_rain[ii] > 3:
            fig.text(ii, historical_rain[ii]-.8, s=str(historical_rain[ii])[:4])
        else:
            fig.text(ii, historical_rain[ii]+.2, s=str(historical_rain[ii])[:4])

    plt.ylabel('Rain (mm)')
    plt.savefig(os.path.expanduser(img_path))


def main():
    today_date = datetime.combine(datetime.now().astimezone(timezone(TIMEZONE)).date(),
                                  datetime.min.time())

    # get precipitation for all hours in the range we're interested in
    historical_days = [today_date - timedelta(days=ii) for ii in [4, 3, 2, 1, 0]]
    historical_rain_hours = []
    for hist_day in historical_days:
        historical_rain_hours += get_rain_hours(get_weather_for_date(hist_day))

    # exclude today (local) hours
    filtered_rain_hours = [x for x in historical_rain_hours
                           if today_date.date() - timedelta(days=5) <
                           list(x.keys())[0].date()
                           < today_date.date()]

    rain = total_rain(filtered_rain_hours)
    pretty_today = today_date.strftime('%b %d, %Y')

    if rain > 0:
        message = f'Good morning! Here is your rain report for {pretty_today}: ' \
                  f'{rain}mm of rain over the past 4 days.'
    else:
        message = f'Good morning! Today is {pretty_today} ' \
                  'and there was no rain over the past 4 days.'

    save_plot_for_rain(today_date, filtered_rain_hours, '~/projects/spritz/rain.png')

    send_message(message, 'Do you need to Spritz that Shit?', '~/projects/spritz/rain.png')


if __name__ == '__main__':
    main()
