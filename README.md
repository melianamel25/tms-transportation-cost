# Mini TMS Transport Costing

Aplikasi Streamlit untuk simulasi Transportation Management System berbasis data:

- Master customer, pool, vehicle group, vehicle unit, driver, route, fuel, dan cost parameter.
- Costing quotation berdasarkan kombinasi `Origin + Destination + Vehicle Group`.
- Quotation dan sales order.
- Dispatch setelah quotation disetujui, termasuk assignment kendaraan aktual dan driver.
- Dashboard dan report fleet, revenue, route, serta utilization.

## Menjalankan

```powershell
streamlit run app.py --server.port 8502
```

Data awal akan dibuat otomatis di folder `data/` saat aplikasi pertama kali dijalankan.
