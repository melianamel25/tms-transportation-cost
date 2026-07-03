from __future__ import annotations

import math
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FUEL_PRICE_DEFAULT = 6800
ORDER_STATUSES = ["Requested", "Costed", "Quoted", "Deal", "Cancelled"]
QUOTE_STATUSES = ["Draft", "Sent", "Approved", "Rejected", "Expired"]
DISPATCH_STATUSES = ["Planned", "Assigned", "In Transit", "Completed", "Cancelled"]


TABLES: dict[str, list[str]] = {
    "customers": ["customer_id", "customer_name", "segment", "city", "pic", "phone", "status"],
    "pools": ["pool_id", "pool_name", "city", "province", "status"],
    "vehicle_groups": [
        "vehicle_group",
        "capacity_ton",
        "fuel_km_per_liter",
        "maintenance_per_km",
        "depreciation_per_km",
        "driver_allowance_per_day",
        "overhead_percent",
        "margin_percent",
        "status",
    ],
    "vehicle_units": [
        "unit_id",
        "plate_no",
        "vehicle_group",
        "capacity_ton",
        "year",
        "pool",
        "fuel_km_per_liter",
        "status",
    ],
    "drivers": ["driver_id", "driver_name", "pool", "sim_type", "phone", "status"],
    "routes": ["route_id", "origin", "destination", "km", "toll", "estimate_hours", "zone", "status"],
    "cost_parameters": ["parameter", "value", "unit", "notes"],
    "orders": [
        "order_id",
        "order_date",
        "customer_id",
        "customer_name",
        "origin",
        "destination",
        "vehicle_group",
        "cargo_weight_ton",
        "trip_type",
        "status",
        "notes",
    ],
    "costings": [
        "costing_id",
        "order_id",
        "route_id",
        "vehicle_group",
        "km",
        "fuel_cost",
        "toll",
        "maintenance_cost",
        "depreciation_cost",
        "driver_allowance",
        "overhead",
        "base_cost",
        "margin",
        "recommended_price",
        "created_at",
    ],
    "quotations": [
        "quotation_id",
        "costing_id",
        "order_id",
        "customer_name",
        "route",
        "vehicle_group",
        "quoted_price",
        "status",
        "valid_until",
        "created_at",
    ],
    "sales_orders": ["sales_order_id", "quotation_id", "order_id", "customer_name", "value", "status", "created_at"],
    "dispatch": [
        "dispatch_id",
        "sales_order_id",
        "route",
        "vehicle_group",
        "unit_id",
        "plate_no",
        "driver_id",
        "driver_name",
        "pool",
        "status",
        "planned_date",
    ],
    "history": ["timestamp", "entity", "entity_id", "activity", "notes"],
}


def money(value: float | int) -> str:
    return f"Rp{float(value):,.0f}".replace(",", ".")


def table_path(name: str) -> Path:
    return DATA_DIR / f"{name}.csv"


def load_table(name: str) -> pd.DataFrame:
    path = table_path(name)
    if not path.exists():
        return pd.DataFrame(columns=TABLES[name])
    df = pd.read_csv(path)
    for column in TABLES[name]:
        if column not in df.columns:
            df[column] = ""
    return df[TABLES[name]]


def save_table(name: str, df: pd.DataFrame) -> None:
    df = df.copy()
    for column in TABLES[name]:
        if column not in df.columns:
            df[column] = ""
    df[TABLES[name]].to_csv(table_path(name), index=False)


def next_id(df: pd.DataFrame, prefix: str, column: str) -> str:
    if df.empty or column not in df:
        return f"{prefix}0001"
    numbers = (
        df[column]
        .astype(str)
        .str.extract(r"(\d+)$")[0]
        .dropna()
        .astype(int)
    )
    current = int(numbers.max()) if not numbers.empty else 0
    return f"{prefix}{current + 1:04d}"


def add_history(entity: str, entity_id: str, activity: str, notes: str = "") -> None:
    history = load_table("history")
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entity": entity,
        "entity_id": entity_id,
        "activity": activity,
        "notes": notes,
    }
    save_table("history", pd.concat([history, pd.DataFrame([row])], ignore_index=True))


def seed_data() -> None:
    if table_path("vehicle_units").exists():
        return

    customers = pd.DataFrame(
        [
            ["CUST0001", "PT Nusantara Retail", "Retail", "Jakarta", "Ibu Rina", "0812-1000-0001", "Active"],
            ["CUST0002", "PT Jawa FMCG", "FMCG", "Surabaya", "Pak Arif", "0812-1000-0002", "Active"],
            ["CUST0003", "CV Bandung Distribusi", "Distributor", "Bandung", "Ibu Maya", "0812-1000-0003", "Active"],
            ["CUST0004", "PT Semarang Tekstil", "Manufacturing", "Semarang", "Pak Dani", "0812-1000-0004", "Active"],
        ],
        columns=TABLES["customers"],
    )
    save_table("customers", customers)

    pools = pd.DataFrame(
        [
            ["POOL01", "Jakarta", "Jakarta", "DKI Jakarta", "Active"],
            ["POOL02", "Cikarang", "Cikarang", "Jawa Barat", "Active"],
            ["POOL03", "Bandung", "Bandung", "Jawa Barat", "Active"],
            ["POOL04", "Semarang", "Semarang", "Jawa Tengah", "Active"],
            ["POOL05", "Surabaya", "Surabaya", "Jawa Timur", "Active"],
            ["POOL06", "Malang", "Malang", "Jawa Timur", "Active"],
        ],
        columns=TABLES["pools"],
    )
    save_table("pools", pools)

    groups = pd.DataFrame(
        [
            ["CDE", 2.0, 10.0, 1500, 800, 175000, 8, 18, "Active"],
            ["CDD", 5.0, 8.0, 2000, 1000, 225000, 8, 20, "Active"],
            ["Wingbox", 8.0, 5.0, 3500, 2000, 300000, 9, 22, "Active"],
            ["Trailer", 20.0, 3.0, 5000, 3500, 450000, 10, 25, "Active"],
        ],
        columns=TABLES["vehicle_groups"],
    )
    save_table("vehicle_groups", groups)

    routes = pd.DataFrame(
        [
            ["RT0001", "Jakarta", "Bandung", 145, 125000, 3, "Jawa Barat", "Active"],
            ["RT0002", "Jakarta", "Semarang", 450, 390000, 8, "Jawa Tengah", "Active"],
            ["RT0003", "Jakarta", "Surabaya", 780, 710000, 14, "Jawa Timur", "Active"],
            ["RT0004", "Bandung", "Semarang", 360, 315000, 7, "Jawa Tengah", "Active"],
            ["RT0005", "Semarang", "Surabaya", 350, 305000, 6, "Jawa Timur", "Active"],
            ["RT0006", "Surabaya", "Malang", 95, 85000, 2, "Jawa Timur", "Active"],
            ["RT0007", "Cikarang", "Bandung", 125, 110000, 3, "Jawa Barat", "Active"],
            ["RT0008", "Cikarang", "Surabaya", 760, 690000, 14, "Jawa Timur", "Active"],
        ],
        columns=TABLES["routes"],
    )
    save_table("routes", routes)

    params = pd.DataFrame(
        [
            ["fuel_price", FUEL_PRICE_DEFAULT, "Rp/liter", "Harga solar acuan"],
            ["rounding", 10000, "Rp", "Pembulatan harga quotation"],
            ["min_margin_percent", 15, "%", "Margin minimal komersial"],
        ],
        columns=TABLES["cost_parameters"],
    )
    save_table("cost_parameters", params)

    pool_names = pools["pool_name"].tolist()
    group_rows = groups.to_dict("records")
    status_cycle = ["Ready"] * 78 + ["In Use"] * 14 + ["Maintenance"] * 6 + ["Inactive"] * 2
    units = []
    unit_no = 1
    group_mix = [("CDE", 650), ("CDD", 850), ("Wingbox", 500), ("Trailer", 200)]
    group_lookup = {row["vehicle_group"]: row for row in group_rows}
    for group_name, count in group_mix:
        group = group_lookup[group_name]
        for index in range(count):
            pool = pool_names[(unit_no + index) % len(pool_names)]
            units.append(
                [
                    f"VH{unit_no:05d}",
                    f"B{1000 + (unit_no % 8999)}{chr(65 + unit_no % 26)}{chr(65 + (unit_no // 26) % 26)}",
                    group_name,
                    group["capacity_ton"],
                    2018 + (unit_no % 7),
                    pool,
                    max(2.5, float(group["fuel_km_per_liter"]) - ((unit_no % 5) * 0.2)),
                    status_cycle[unit_no % len(status_cycle)],
                ]
            )
            unit_no += 1
    save_table("vehicle_units", pd.DataFrame(units, columns=TABLES["vehicle_units"]))

    drivers = []
    for driver_no in range(1, 2301):
        pool = pool_names[driver_no % len(pool_names)]
        sim = "B2 Umum" if driver_no % 6 == 0 else "B1 Umum"
        status = "Available" if driver_no % 10 not in (0, 1) else "Assigned"
        drivers.append([f"DRV{driver_no:05d}", f"Driver {driver_no:05d}", pool, sim, f"0813-{driver_no:04d}-{driver_no % 10000:04d}", status])
    save_table("drivers", pd.DataFrame(drivers, columns=TABLES["drivers"]))

    for name in ["orders", "costings", "quotations", "sales_orders", "dispatch", "history"]:
        save_table(name, pd.DataFrame(columns=TABLES[name]))


def parameter_value(name: str, fallback: float) -> float:
    params = load_table("cost_parameters")
    row = params.loc[params["parameter"].eq(name)]
    if row.empty:
        return fallback
    return float(row.iloc[0]["value"])


def find_route(origin: str, destination: str) -> pd.Series | None:
    routes = load_table("routes")
    exact = routes.loc[
        routes["origin"].astype(str).str.casefold().eq(origin.casefold())
        & routes["destination"].astype(str).str.casefold().eq(destination.casefold())
        & routes["status"].eq("Active")
    ]
    if not exact.empty:
        return exact.iloc[0]
    reverse = routes.loc[
        routes["origin"].astype(str).str.casefold().eq(destination.casefold())
        & routes["destination"].astype(str).str.casefold().eq(origin.casefold())
        & routes["status"].eq("Active")
    ]
    if not reverse.empty:
        return reverse.iloc[0]
    return None


def calculate_costing(route: pd.Series, group: pd.Series) -> dict[str, float]:
    fuel_price = parameter_value("fuel_price", FUEL_PRICE_DEFAULT)
    rounding = parameter_value("rounding", 10000)
    km = float(route["km"])
    days = max(1, math.ceil(float(route["estimate_hours"]) / 10))
    fuel_cost = km / float(group["fuel_km_per_liter"]) * fuel_price
    maintenance_cost = km * float(group["maintenance_per_km"])
    depreciation_cost = km * float(group["depreciation_per_km"])
    driver_allowance = days * float(group["driver_allowance_per_day"])
    toll = float(route["toll"])
    direct_cost = fuel_cost + maintenance_cost + depreciation_cost + driver_allowance + toll
    overhead = direct_cost * float(group["overhead_percent"]) / 100
    base_cost = direct_cost + overhead
    margin = base_cost * float(group["margin_percent"]) / 100
    recommended = math.ceil((base_cost + margin) / rounding) * rounding
    return {
        "km": km,
        "fuel_cost": fuel_cost,
        "toll": toll,
        "maintenance_cost": maintenance_cost,
        "depreciation_cost": depreciation_cost,
        "driver_allowance": driver_allowance,
        "overhead": overhead,
        "base_cost": base_cost,
        "margin": margin,
        "recommended_price": recommended,
    }


def metric_card(label: str, value: str, caption: str = "") -> None:
    st.metric(label, value, help=caption or None)


def page_dashboard() -> None:
    st.title("Dashboard TMS")
    units = load_table("vehicle_units")
    quotations = load_table("quotations")
    sales_orders = load_table("sales_orders")
    dispatch = load_table("dispatch")

    ready = int(units["status"].eq("Ready").sum()) if not units.empty else 0
    maintenance = int(units["status"].eq("Maintenance").sum()) if not units.empty else 0
    revenue = pd.to_numeric(sales_orders.get("value", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    active_dispatch = int(dispatch["status"].isin(["Planned", "Assigned", "In Transit"]).sum()) if not dispatch.empty else 0

    cols = st.columns(4)
    cols[0].metric("Total Unit", f"{len(units):,}".replace(",", "."))
    cols[1].metric("Ready", f"{ready:,}".replace(",", "."))
    cols[2].metric("Maintenance", f"{maintenance:,}".replace(",", "."))
    cols[3].metric("Active Dispatch", active_dispatch)

    cols = st.columns(2)
    with cols[0]:
        st.subheader("Fleet by Status")
        chart = units.groupby(["vehicle_group", "status"]).size().reset_index(name="unit")
        if not chart.empty:
            st.bar_chart(chart, x="vehicle_group", y="unit", color="status")
    with cols[1]:
        st.subheader("Commercial Pipeline")
        if quotations.empty:
            st.info("Belum ada quotation.")
        else:
            pipe = quotations.groupby("status")["quotation_id"].count().reset_index(name="count")
            st.bar_chart(pipe, x="status", y="count")

    st.subheader("Ringkasan Revenue")
    st.write(f"Total sales order approved: **{money(revenue)}**")


def page_master_data() -> None:
    st.title("Master Data")
    tabs = st.tabs(["Customer", "Vehicle Group", "Vehicle Unit", "Driver", "Pool", "Route", "Cost Parameter"])
    mapping = [
        ("customers", tabs[0]),
        ("vehicle_groups", tabs[1]),
        ("vehicle_units", tabs[2]),
        ("drivers", tabs[3]),
        ("pools", tabs[4]),
        ("routes", tabs[5]),
        ("cost_parameters", tabs[6]),
    ]
    for table, tab in mapping:
        with tab:
            df = load_table(table)
            st.caption(f"{len(df):,} records".replace(",", "."))
            if table in {"vehicle_units", "drivers"}:
                left, right = st.columns([1, 1])
                with left:
                    keyword = st.text_input("Cari", key=f"search_{table}")
                with right:
                    status_options = ["All"] + sorted(df["status"].dropna().astype(str).unique().tolist())
                    status = st.selectbox("Status", status_options, key=f"status_{table}")
                view = df.copy()
                if keyword:
                    mask = view.astype(str).apply(lambda col: col.str.contains(keyword, case=False, na=False)).any(axis=1)
                    view = view[mask]
                if status != "All":
                    view = view.loc[view["status"].eq(status)]
                st.dataframe(view.head(500), use_container_width=True, hide_index=True)
                st.caption("Untuk performa, tabel besar ditampilkan maksimal 500 baris terfilter.")
            else:
                edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", hide_index=True, key=f"editor_{table}")
                if st.button("Simpan perubahan", key=f"save_{table}"):
                    save_table(table, edited)
                    add_history("master", table, "Updated master data", f"{len(edited)} rows")
                    st.success("Master data tersimpan.")


def page_order_costing() -> None:
    st.title("Order Request & Costing")
    customers = load_table("customers")
    routes = load_table("routes")
    groups = load_table("vehicle_groups")
    orders = load_table("orders")
    costings = load_table("costings")

    with st.form("new_order"):
        st.subheader("Buat Order Request")
        customer_name = st.selectbox("Customer", customers["customer_name"].tolist())
        route_label = st.selectbox(
            "Route",
            routes.apply(lambda row: f"{row['origin']} -> {row['destination']} ({row['km']} km)", axis=1).tolist(),
        )
        vehicle_group = st.selectbox("Vehicle Group", groups["vehicle_group"].tolist())
        cargo_weight = st.number_input("Berat muatan (ton)", min_value=0.0, value=1.0, step=0.5)
        trip_type = st.selectbox("Trip Type", ["One Way", "Round Trip"])
        notes = st.text_area("Catatan")
        submit = st.form_submit_button("Hitung & Simpan Costing")

    if submit:
        selected_route = routes.iloc[routes.apply(lambda row: f"{row['origin']} -> {row['destination']} ({row['km']} km)", axis=1).tolist().index(route_label)]
        selected_group = groups.loc[groups["vehicle_group"].eq(vehicle_group)].iloc[0]
        customer = customers.loc[customers["customer_name"].eq(customer_name)].iloc[0]
        if cargo_weight > float(selected_group["capacity_ton"]):
            st.error("Berat muatan melebihi kapasitas vehicle group.")
            return
        calc = calculate_costing(selected_route, selected_group)
        if trip_type == "Round Trip":
            for key in ["fuel_cost", "toll", "maintenance_cost", "depreciation_cost", "driver_allowance", "overhead", "base_cost", "margin", "recommended_price"]:
                calc[key] *= 2
            calc["km"] *= 2

        order_id = next_id(orders, "ORD", "order_id")
        costing_id = next_id(costings, "CST", "costing_id")
        order_row = {
            "order_id": order_id,
            "order_date": date.today().isoformat(),
            "customer_id": customer["customer_id"],
            "customer_name": customer_name,
            "origin": selected_route["origin"],
            "destination": selected_route["destination"],
            "vehicle_group": vehicle_group,
            "cargo_weight_ton": cargo_weight,
            "trip_type": trip_type,
            "status": "Costed",
            "notes": notes,
        }
        costing_row = {
            "costing_id": costing_id,
            "order_id": order_id,
            "route_id": selected_route["route_id"],
            "vehicle_group": vehicle_group,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **calc,
        }
        save_table("orders", pd.concat([orders, pd.DataFrame([order_row])], ignore_index=True))
        save_table("costings", pd.concat([costings, pd.DataFrame([costing_row])], ignore_index=True))
        add_history("order", order_id, "Created order and costing", costing_id)
        st.success(f"Costing {costing_id} tersimpan. Rekomendasi harga: {money(calc['recommended_price'])}")

    st.subheader("Costing Terakhir")
    latest = load_table("costings").tail(20).sort_values("created_at", ascending=False)
    st.dataframe(latest, use_container_width=True, hide_index=True)


def page_quotation() -> None:
    st.title("Quotation")
    costings = load_table("costings")
    orders = load_table("orders")
    quotations = load_table("quotations")
    sales_orders = load_table("sales_orders")

    if costings.empty:
        st.info("Belum ada costing. Buat costing dari menu Order Request & Costing.")
        return

    merged = costings.merge(orders, on="order_id", how="left", suffixes=("", "_order"))
    merged["label"] = merged.apply(
        lambda row: f"{row['costing_id']} | {row['customer_name']} | {row['origin']} -> {row['destination']} | {row['vehicle_group']} | {money(row['recommended_price'])}",
        axis=1,
    )
    with st.form("new_quote"):
        costing_label = st.selectbox("Pilih Costing", merged["label"].tolist())
        selected = merged.loc[merged["label"].eq(costing_label)].iloc[0]
        quoted_price = st.number_input("Harga Quotation", min_value=0.0, value=float(selected["recommended_price"]), step=50000.0)
        valid_until = st.date_input("Valid Until", value=date.today().replace(day=min(date.today().day, 28)))
        status = st.selectbox("Status", QUOTE_STATUSES)
        submit = st.form_submit_button("Generate Quotation")

    if submit:
        quotation_id = next_id(quotations, "QTN", "quotation_id")
        route = f"{selected['origin']} -> {selected['destination']}"
        quote_row = {
            "quotation_id": quotation_id,
            "costing_id": selected["costing_id"],
            "order_id": selected["order_id"],
            "customer_name": selected["customer_name"],
            "route": route,
            "vehicle_group": selected["vehicle_group"],
            "quoted_price": quoted_price,
            "status": status,
            "valid_until": valid_until.isoformat(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_table("quotations", pd.concat([quotations, pd.DataFrame([quote_row])], ignore_index=True))
        add_history("quotation", quotation_id, "Generated quotation", route)
        if status == "Approved":
            sales_order_id = next_id(sales_orders, "SO", "sales_order_id")
            so_row = {
                "sales_order_id": sales_order_id,
                "quotation_id": quotation_id,
                "order_id": selected["order_id"],
                "customer_name": selected["customer_name"],
                "value": quoted_price,
                "status": "Open",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            save_table("sales_orders", pd.concat([sales_orders, pd.DataFrame([so_row])], ignore_index=True))
            add_history("sales_order", sales_order_id, "Created from approved quotation", quotation_id)
        st.success(f"Quotation {quotation_id} tersimpan.")

    st.subheader("Quotation List")
    quote_df = load_table("quotations")
    edited = st.data_editor(quote_df, use_container_width=True, hide_index=True, num_rows="dynamic")
    if st.button("Simpan Quotation List"):
        save_table("quotations", edited)
        st.success("Quotation list tersimpan.")

    st.download_button(
        "Download Quotation CSV",
        data=load_table("quotations").to_csv(index=False).encode("utf-8"),
        file_name="quotations.csv",
        mime="text/csv",
    )


def page_dispatch() -> None:
    st.title("Dispatch")
    sales_orders = load_table("sales_orders")
    dispatch = load_table("dispatch")
    quotations = load_table("quotations")
    units = load_table("vehicle_units")
    drivers = load_table("drivers")

    open_so = sales_orders.loc[sales_orders["status"].isin(["Open", "Planned"])] if not sales_orders.empty else sales_orders
    if open_so.empty:
        st.info("Belum ada sales order open. Approve quotation terlebih dahulu.")
    else:
        joined = open_so.merge(quotations, on=["quotation_id", "order_id", "customer_name"], how="left")
        joined["label"] = joined.apply(lambda row: f"{row['sales_order_id']} | {row['customer_name']} | {row['route']} | {row['vehicle_group']}", axis=1)
        with st.form("new_dispatch"):
            so_label = st.selectbox("Sales Order", joined["label"].tolist())
            selected = joined.loc[joined["label"].eq(so_label)].iloc[0]
            available_units = units.loc[
                units["vehicle_group"].eq(selected["vehicle_group"]) & units["status"].eq("Ready")
            ].copy()
            pool_options = ["All"] + sorted(available_units["pool"].dropna().unique().tolist())
            pool = st.selectbox("Pool Preferensi", pool_options)
            if pool != "All":
                available_units = available_units.loc[available_units["pool"].eq(pool)]
            if available_units.empty:
                st.warning("Tidak ada unit Ready untuk kombinasi vehicle group dan pool ini.")
                st.form_submit_button("Assign Dispatch", disabled=True)
                return
            unit_label = st.selectbox(
                "Unit Kendaraan",
                available_units.apply(lambda row: f"{row['unit_id']} | {row['plate_no']} | {row['pool']}", axis=1).tolist(),
            )
            selected_unit = available_units.iloc[
                available_units.apply(lambda row: f"{row['unit_id']} | {row['plate_no']} | {row['pool']}", axis=1).tolist().index(unit_label)
            ]
            available_drivers = drivers.loc[drivers["pool"].eq(selected_unit["pool"]) & drivers["status"].eq("Available")]
            if available_drivers.empty:
                st.warning("Tidak ada driver Available di pool unit terpilih.")
                st.form_submit_button("Assign Dispatch", disabled=True)
                return
            driver_label = st.selectbox(
                "Driver",
                available_drivers.apply(lambda row: f"{row['driver_id']} | {row['driver_name']} | {row['pool']}", axis=1).tolist(),
            )
            planned_date = st.date_input("Planned Date", value=date.today())
            submit = st.form_submit_button("Assign Dispatch")

        if submit:
            selected_driver = available_drivers.iloc[
                available_drivers.apply(lambda row: f"{row['driver_id']} | {row['driver_name']} | {row['pool']}", axis=1).tolist().index(driver_label)
            ]
            dispatch_id = next_id(dispatch, "DSP", "dispatch_id")
            row = {
                "dispatch_id": dispatch_id,
                "sales_order_id": selected["sales_order_id"],
                "route": selected["route"],
                "vehicle_group": selected["vehicle_group"],
                "unit_id": selected_unit["unit_id"],
                "plate_no": selected_unit["plate_no"],
                "driver_id": selected_driver["driver_id"],
                "driver_name": selected_driver["driver_name"],
                "pool": selected_unit["pool"],
                "status": "Assigned",
                "planned_date": planned_date.isoformat(),
            }
            save_table("dispatch", pd.concat([dispatch, pd.DataFrame([row])], ignore_index=True))
            units.loc[units["unit_id"].eq(selected_unit["unit_id"]), "status"] = "In Use"
            drivers.loc[drivers["driver_id"].eq(selected_driver["driver_id"]), "status"] = "Assigned"
            sales_orders.loc[sales_orders["sales_order_id"].eq(selected["sales_order_id"]), "status"] = "Planned"
            save_table("vehicle_units", units)
            save_table("drivers", drivers)
            save_table("sales_orders", sales_orders)
            add_history("dispatch", dispatch_id, "Assigned vehicle and driver", selected["sales_order_id"])
            st.success(f"Dispatch {dispatch_id} assigned.")

    st.subheader("Dispatch List")
    edited = st.data_editor(load_table("dispatch"), use_container_width=True, hide_index=True, num_rows="dynamic")
    if st.button("Simpan Dispatch List"):
        save_table("dispatch", edited)
        st.success("Dispatch list tersimpan.")


def page_reports() -> None:
    st.title("Reports")
    units = load_table("vehicle_units")
    costings = load_table("costings")
    quotations = load_table("quotations")
    sales_orders = load_table("sales_orders")
    routes = load_table("routes")

    tabs = st.tabs(["Fleet", "Revenue", "Cost Analysis", "Route"])
    with tabs[0]:
        st.subheader("Vehicle Utilization")
        util = units.groupby(["pool", "status"]).size().reset_index(name="unit")
        st.bar_chart(util, x="pool", y="unit", color="status")
        st.dataframe(util, use_container_width=True, hide_index=True)
    with tabs[1]:
        revenue = pd.to_numeric(sales_orders.get("value", pd.Series(dtype=float)), errors="coerce").fillna(0)
        st.metric("Revenue Sales Order", money(revenue.sum()))
        st.dataframe(sales_orders, use_container_width=True, hide_index=True)
    with tabs[2]:
        if costings.empty:
            st.info("Belum ada costing.")
        else:
            summary = costings.groupby("vehicle_group")[["base_cost", "margin", "recommended_price"]].mean().reset_index()
            st.bar_chart(summary, x="vehicle_group", y=["base_cost", "margin", "recommended_price"])
            st.dataframe(summary, use_container_width=True, hide_index=True)
    with tabs[3]:
        route_quote = quotations.groupby("route")["quotation_id"].count().reset_index(name="quotation_count") if not quotations.empty else pd.DataFrame()
        st.dataframe(routes, use_container_width=True, hide_index=True)
        if not route_quote.empty:
            st.subheader("Quotation by Route")
            st.bar_chart(route_quote, x="route", y="quotation_count")


def main() -> None:
    st.set_page_config(page_title="Mini TMS Transport Costing", page_icon="TMS", layout="wide")
    seed_data()

    st.sidebar.title("Mini TMS")
    st.sidebar.caption("Costing berdasarkan Route + Vehicle Group")
    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Master Data", "Order & Costing", "Quotation", "Dispatch", "Reports", "History"],
    )

    if page == "Dashboard":
        page_dashboard()
    elif page == "Master Data":
        page_master_data()
    elif page == "Order & Costing":
        page_order_costing()
    elif page == "Quotation":
        page_quotation()
    elif page == "Dispatch":
        page_dispatch()
    elif page == "Reports":
        page_reports()
    else:
        st.title("History")
        st.dataframe(load_table("history").sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
