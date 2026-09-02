import React, { useState } from "react";
import { Typography, Button, TextField, CircularProgress, Alert } from "@mui/material";
import { Bar } from "react-chartjs-2";
import { analyzeSentiment } from "../services/api";

function Sentiment() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeSentiment(text);
      setResult(data);
    } catch (err) {
      setError("Failed to fetch sentiment: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [{
      label: "Sentiment Score",
      data: [result.positive, result.negative, result.neutral],
      backgroundColor: ["green", "red", "gray"]
    }]
  } : null;

  return (
    <div>
      <Typography variant="h5">Sentiment Analysis</Typography>
      <TextField
        label="Enter headline"
        value={text}
        onChange={(e) => setText(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button variant="contained" color="primary" onClick={handleAnalyze}>
        Analyze
      </Button>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      {chartData && <Bar data={chartData} />}
    </div>
  );
}

export default Sentiment;
