import React, { useState } from "react";
import { Typography, Button, CircularProgress, Alert } from "@mui/material";
import { runFundamentals } from "../services/api";

function Fundamentals() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const X = [[1,2],[2,3],[3,4]];
      const y = [10,20,30];
      const res = await runFundamentals(X, y);
      setData(res.prediction.map((p, i) => ({ id: i, value: p })));
    } catch (err) {
      setError("Failed to fetch fundamentals: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Typography variant="h5">Fundamentals Analysis</Typography>
      <Button variant="contained" color="primary" onClick={handleRun}>
        Run
      </Button>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      {data.length > 0 && (
        <table border="1" style={{ marginTop: "10px", width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Prediction</th>
            </tr>
          </thead>
          <tbody>
            {data.map(row => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Fundamentals;
