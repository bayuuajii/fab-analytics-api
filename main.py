import os
import sqlite3
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Fab Yield Analytics API",
    description="REST API Microservice for Semiconductor Yield & SPC Monitoring",
    version="1.0.0"
)

# Path mengarah ke database di repo ke-2 (fab-data-pipeline)
DB_PATH = os.path.expanduser("~/fab-data-pipeline/fab_data.db")

@app.get("/")
def read_root():
    return {
        "service": "Fab Analytics API Engine",
        "status": "ONLINE",
        "architecture": "Microservices"
    }

@app.get("/api/v1/yield")
def get_yield_metrics():
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=404, 
            detail="Database fab_data.db tidak ditemukan. Pastikan pipeline repo ke-2 sudah pernah dijalankan."
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hitung total siklus
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs")
    total_data = cursor.fetchone()[0]

    if total_data == 0:
        conn.close()
        return {"message": "Database masih kosong."}

    # Hitung siklus normal vs error
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs WHERE spc_status = 'IN_CONTROL'")
    in_control = cursor.fetchone()[0]
    out_of_control = total_data - in_control
    yield_percentage = round((in_control / total_data) * 100, 2)

    conn.close()

    return {
        "equipment_id": "LITHO-01",
        "metrics": {
            "total_cycles": total_data,
            "in_control_cycles": in_control,
            "out_of_control_cycles": out_of_control,
            "yield_percentage": yield_percentage
        },
        "factory_status": "OPTIMAL" if yield_percentage >= 95.0 else "WARNING_NEEDS_INSPECTION"
    }
