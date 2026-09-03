// src/services/api.js

import CONFIG from "../config";

const BASE_URL = CONFIG.API_BASE_URL;


/**
 * Generic helper for API requests
 */
async function request(endpoint, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    if (!response.ok) {
      throw new Error(`Backend error ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`API request failed: ${endpoint}`, err);
    throw err;
  }
}

/**
 * Sentiment Analysis
 * @param {string} text - headline or sentence
 */
export async function analyzeSentiment(text) {
  return request("/sentiment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
}

/**
 * Forecast
 * @param {number[]} data - historical price series
 */
export async function forecastStock(data) {
  return request("/forecast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data })
  });
}

/**
 * Fundamentals
 * @param {number[][]} X - feature matrix
 * @param {number[]} y - target values
 */
export async function runFundamentals(X, y) {
  return request("/fundamentals", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ X, y })
  });
}

/**
 * Portfolio Optimization
 * @param {number[]} returns - expected returns
 * @param {number[][]} cov_matrix - covariance matrix
 */
export async function optimizePortfolio(returns, cov_matrix) {
  return request("/portfolio", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ returns, cov_matrix })
  });
}

/**
 * Recommendation from model outputs and price history
 * @param {{sentiment: Object, prices: number[], forecast: number[], fundamentals: number[]}} data
 */
export async function analyzeRecommendation(data) {
  return request("/recommendation/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}
