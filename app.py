from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city, country="uk"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{country}&appid={WEATHER_API_KEY}&units=metric&cnt=56"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return None

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        daily = {}
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in daily:
                from datetime import datetime
                day_name = day_names[datetime.strptime(date, "%Y-%m-%d").weekday()]
                daily[day_name] = {
                    "temp": round(item["main"]["temp"]),
                    "description": item["weather"][0]["description"].title(),
                    "icon": item["weather"][0]["icon"],
                    "rain": round(item.get("pop", 0) * 100)
                }

        return daily
    except:
        return None

def create_plan(total_km, rest_days):
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days = [d for d in day_order if d not in rest_days]

    if len(days) == 0:
        return None, "You need at least one running day!"

    has_wednesday = "Wed" in days
    wed_km = 8.0 if total_km >= 25 else None
    long_run = round(min(20, max(15, total_km * 0.35)), 1)

    min_possible = ((wed_km or 1) if has_wednesday else 1) + (long_run if len(days) > 1 else 0) + (1 * max(0, len(days) - 2))
    if total_km < min_possible:
        return None, f"Total km is too low for {len(days)} days. You need at least {min_possible}km."

    if "Sun" in days:
        long_run_day = "Sun"
    else:
        for preferred in ["Sat", "Fri", "Thu", "Tue", "Mon"]:
            if preferred in days and preferred != "Wed":
                long_run_day = preferred
                break
    if has_wednesday and not wed_km:
        days.remove("Wed")
        has_wednesday = False

    fixed_km = ((wed_km or 0) if has_wednesday else 0) + long_run
    remaining_km = total_km - fixed_km
    other_days = [d for d in days if d != "Wed" and d != long_run_day]
    num_other = len(other_days)

    if num_other > 0:
        avg = remaining_km / num_other
        base_offsets = [-1.5, -0.5, 0.5, 1.5, 1.0, -1.0, 0.0][:num_other]
        offset_avg = sum(base_offsets) / num_other
        normalized = [v - offset_avg for v in base_offsets]
        varied = [round(max(1.0, avg + v), 1) for v in normalized]
        varied[-1] = round(remaining_km - sum(varied[:-1]), 1)
    else:
        varied = []

    plan = {}
    for i, day in enumerate(other_days):
        plan[day] = varied[i]
    if has_wednesday and wed_km:
        plan["Wed"] = wed_km
    plan[long_run_day] = long_run

    result = [{"day": day, "km": plan[day]} for day in days]
    return result, None

@app.route("/", methods=["GET", "POST"])
def index():
    weeks = None
    error = None
    start_km = None
    end_km = None
    weather = None
    city = None

    if request.method == "POST":
        start_km = float(request.form["start_km"])
        end_km = float(request.form["end_km"])
        rest_days = request.form.getlist("rest_days")
        city = request.form.get("city", "").strip()
        country = request.form.get("country", "uk")

        if city:
            weather = get_weather(city, country)

        step = (end_km - start_km) / 3
        weekly_targets = [round(start_km + step * i, 1) for i in range(4)]

        weeks = []
        for i, km in enumerate(weekly_targets):
            plan, err = create_plan(km, rest_days)
            if err:
                error = f"Week {i+1}: {err}"
                weeks = None
                break
            weeks.append({"week": i + 1, "total_km": km, "runs": plan})

    return render_template("index.html", weeks=weeks, error=error, start_km=start_km, end_km=end_km, weather=weather, city=city, country=request.form.get("country", "uk") if request.method == "POST" else "uk")

if __name__ == "__main__":
    app.run(debug=True)