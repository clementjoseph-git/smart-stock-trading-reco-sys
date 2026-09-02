import React, { useState } from "react";
import { Typography, Button, CircularProgress, Alert } from "@mui/material";
import { Pie } from "react-chartjs-2";
import { optimizePortfolio } from "../services/api";

function Portfolio() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    try {
      const returns = [0.1, 0.2, 0.15];
      const cov_matrix = [[0.1,0.02,0.03],[0.02,0.1,0.04],[0.03,0.04,0.1]];
      const res = await optimizePortfolio(returns, cov_matrix);
      setResult(res);
    } catch (err) {
      setError("Failed to fetch portfolio: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? {
    labels: result.weights.map((_, i) => "Asset " + (i+1)),
    datasets: [{
      data: result.weights,
      backgroundColor: ["orange", "purple", "cyan"]
    }]
  } : null;

  return (
    <div>
      <Typography variant="h5">Portfolio Optimization</Typography>
      <Button variant="contained" color="primary" onClick={handleOptimize}>
        Optimize
      </Button>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      {chartData && <Pie data={chartData} />}
      {result && (
        <div style={{ marginTop: "10px" }}>
          <Typography>Expected Return: {result.expected_return}</Typography>
          <Typography>Risk: {result.risk}</Typography>
        </div>
      )}
    </div>
  );
}

export default Portfolio;
