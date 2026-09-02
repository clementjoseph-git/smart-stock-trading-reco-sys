import React, { useState } from "react";
import { Typography, Button, TextField, CircularProgress, Alert } from "@mui/material";
import { Line } from "react-chartjs-2";
import { forecastStock } from "../services/api";

function Forecast() {
  const [series, setSeries] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = series.split(",").map(Number);
      const res = await forecastStock(data);
      setResult(res.forecast);
    } catch (err) {
      setError("Failed to fetch forecast: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? {
    labels: result.map((_, i) => i + 1),
    datasets: [{
      label: "Forecast",
      data: result,
      borderColor: "blue",
      fill: false
    }]
  } : null;

  return (
    <div>
      <Typography variant="h5">Stock Forecast</Typography>
      <TextField
        label="Comma-separated prices"
        value={series}
        onChange={(e) => setSeries(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button variant="contained" color="primary" onClick={handleForecast}>
        Forecast
      </Button>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      {chartData && <Line data={chartData} />}
    </div>
  );
}

export default Forecast;
