import React, { useState } from "react";
import { Alert, Button, CircularProgress, TextField, Typography } from "@mui/material";
import { analyzeRecommendation } from "../services/api";

function parseNumbers(value) {
  return value.split(",").map((item) => Number(item.trim()));
}

function Recommendation() {
  const [sentiment, setSentiment] = useState({ Positive: "0.33", Negative: "0.33", Neutral: "0.34" });
  const [prices, setPrices] = useState("100, 101, 102, 103, 104");
  const [forecast, setForecast] = useState("105, 106");
  const [fundamentals, setFundamentals] = useState("0.5");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await analyzeRecommendation({
        sentiment: Object.fromEntries(
          Object.entries(sentiment).map(([key, value]) => [key, Number(value)])
        ),
        prices: parseNumbers(prices),
        forecast: parseNumbers(forecast),
        fundamentals: parseNumbers(fundamentals)
      });
      setResult(response);
    } catch (err) {
      setError(`Failed to generate recommendation: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Typography variant="h5">AI Recommendation</Typography>
      {Object.keys(sentiment).map((key) => (
        <TextField
          key={key}
          label={`${key} sentiment score`}
          value={sentiment[key]}
          onChange={(event) => setSentiment({ ...sentiment, [key]: event.target.value })}
          type="number"
          inputProps={{ min: 0, max: 1, step: 0.01 }}
          margin="normal"
          sx={{ mr: 1 }}
        />
      ))}
      <TextField label="Price history" value={prices} onChange={(event) => setPrices(event.target.value)} fullWidth margin="normal" />
      <TextField label="Forecast values" value={forecast} onChange={(event) => setForecast(event.target.value)} fullWidth margin="normal" />
      <TextField label="Fundamental predictions" value={fundamentals} onChange={(event) => setFundamentals(event.target.value)} fullWidth margin="normal" />
      <Button variant="contained" onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Generate recommendation"}
      </Button>
      {loading && <CircularProgress size={24} sx={{ ml: 2, verticalAlign: "middle" }} />}
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {result && (
        <div>
          <Typography variant="h6" sx={{ mt: 2 }}>{result.signal}</Typography>
          <Typography>Confidence: {result.confidence}</Typography>
          <Typography>Risk score: {result.risk_score}</Typography>
          <Typography>Target price: {result.target_price}</Typography>
          <Typography>Stop-loss: {result.stop_loss}</Typography>
          <Typography variant="subtitle1" sx={{ mt: 1 }}>Rationale</Typography>
          <ul>{result.rationale.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

export default Recommendation;
