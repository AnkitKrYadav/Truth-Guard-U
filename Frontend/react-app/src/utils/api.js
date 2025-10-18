import axios from "axios";

// Single source of truth for API base URL
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "";

export const postVerify = (claim, agent = "openai") => {
  return axios.post(`${API_BASE_URL}/api/verify`, { claim, agent });
};

const client = axios.create({
  baseURL: API_BASE_URL,
});

export default client;
