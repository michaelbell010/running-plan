def create_running_plan():
    total_km = float(input("How many kilometers do you want to run this week? "))

    print("\nWhich days do you want to REST?")
    print("Options: Mon, Tue, Wed, Thu, Fri, Sat, Sun")
    day_input = input("Enter rest days separated by commas (or press Enter for none): ")

    # Accept common variations
    day_aliases = {
        "monday": "Mon", "mon": "Mon",
        "tuesday": "Tue", "tue": "Tue", "tues": "Tue",
        "wednesday": "Wed", "wed": "Wed",
        "thursday": "Thu", "thu": "Thu", "thurs": "Thu",
        "friday": "Fri", "fri": "Fri",
        "saturday": "Sat", "sat": "Sat",
        "sunday": "Sun", "sun": "Sun"
    }

    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    all_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if day_input.strip() == "":
        rest_days = []
    else:
        raw_rest = [d.strip().lower() for d in day_input.split(",")]
        rest_days = [day_aliases[d] for d in raw_rest if d in day_aliases]

        if len(rest_days) != len(raw_rest):
            print("\nOne or more days weren't recognised. Please use Mon, Tue, Wed, Thu, Fri, Sat, Sun.")
            return

    days = [d for d in all_days if d not in rest_days]

    if len(days) == 0:
        print("\nYou need at least one running day!")
        return

    has_wednesday = "Wed" in days
    wed_km = 8.0
    long_run = round(min(20, max(15, total_km * 0.35)), 1)

    # Check total km is realistic
    min_possible = (wed_km if has_wednesday else 5) + (long_run if len(days) > 1 else 0) + (5 * max(0, len(days) - 2))
    if total_km < min_possible:
        print(f"\nTotal km is too low for {len(days)} days. You need at least {min_possible}km.")
        return

# Sunday is always the long run, otherwise last available day
    if "Sun" in days:
        long_run_day = "Sun"
    else:
        for preferred in ["Sat", "Fri", "Thu", "Tue", "Mon"]:
            if preferred in days and preferred != "Wed":
                long_run_day = preferred
                break

    # Remaining km spread across other days
    fixed_km = (wed_km if has_wednesday else 0) + long_run
    remaining_km = total_km - fixed_km
    other_days = [d for d in days if d != "Wed" and d != long_run_day]
    num_other = len(other_days)

    if num_other > 0:
        avg = remaining_km / num_other
        base_offsets = [-1.5, -0.5, 0.5, 1.5, 1.0, -1.0, 0.0][:num_other]
        offset_avg = sum(base_offsets) / num_other
        normalized = [v - offset_avg for v in base_offsets]
        varied = [round(max(5.0, avg + v), 1) for v in normalized]
        varied[-1] = round(remaining_km - sum(varied[:-1]), 1)
    else:
        varied = []

    # Build the plan
    plan = {}
    for i, day in enumerate(other_days):
        plan[day] = varied[i]
    if has_wednesday:
        plan["Wed"] = wed_km
    plan[long_run_day] = long_run

    print(f"\nYour weekly running plan ({total_km}km over {len(days)} days):\n")
    for day in days:
        print(f"  {day}: {plan[day]}km")

    all_runs = list(plan.values())
    print(f"\nShortest run: {min(all_runs)}km | Longest run: {max(all_runs)}km")
    print(f"Total: {round(sum(all_runs), 1)}km")

create_running_plan()
