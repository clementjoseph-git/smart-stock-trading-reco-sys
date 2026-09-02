// src/config.js

const ENV = process.env.REACT_APP_ENV || "development";

const CONFIG = {
  development: {
    API_BASE_URL: process.env.REACT_APP_API_BASE_URL_DEV
  },
  staging: {
    API_BASE_URL: process.env.REACT_APP_API_BASE_URL_STAGING
  },
  production: {
    API_BASE_URL: process.env.REACT_APP_API_BASE_URL_PROD
  }
};

export default CONFIG[ENV];
