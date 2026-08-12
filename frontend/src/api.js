import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE });

function unwrapError(err) {
  const detail = err?.response?.data?.detail;
  const message = typeof detail === "string" ? detail : err.message || "Something went wrong";
  const wrapped = new Error(message);
  wrapped.status = err?.response?.status;
  return wrapped;
}

export async function listDatasets() {
  try {
    const { data } = await client.get("/datasets");
    return data.datasets;
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function uploadDataset(file, onProgress) {
  const form = new FormData();
  form.append("file", file);
  try {
    const { data } = await client.post("/datasets/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        if (onProgress && evt.total) onProgress(Math.round((evt.loaded / evt.total) * 100));
      },
    });
    return data.dataset;
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function deleteDataset(id) {
  try {
    await client.delete(`/datasets/${id}`);
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function getPreview(id, rows = 15) {
  try {
    const { data } = await client.get(`/datasets/${id}/preview`, { params: { rows } });
    return data;
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function getSummary(id) {
  try {
    const { data } = await client.get(`/datasets/${id}/summary`);
    return data;
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function getChartData(id, column, bins = 10) {
  try {
    const { data } = await client.get(`/datasets/${id}/chart-data`, { params: { column, bins } });
    return data;
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function chatWithDataset(id, question, history) {
  try {
    const { data } = await client.post(`/datasets/${id}/chat`, { question, history });
    return data.answer;
  } catch (err) {
    throw unwrapError(err);
  }
}
