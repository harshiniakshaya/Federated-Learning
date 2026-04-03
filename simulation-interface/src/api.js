import axios from "axios"

export const hospitalA_local = axios.create({
  // baseURL: "http://localhost:8001"
  baseURL: "https://hospital-a-trainer.onrender.com/"
})

export const hospitalA_comm = axios.create({
  // baseURL: "http://localhost:8002"
  baseURL: "https://hospital-a-sync.onrender.com"
})

export const hospitalB_local = axios.create({
  // baseURL: "http://localhost:8003"
  baseURL: "https://hospital-b-trainer.onrender.com"
})

export const hospitalB_comm = axios.create({
  // baseURL: "http://localhost:8004"
  baseURL: "https://hospital-b-sync.onrender.com"
})

export const central = axios.create({
  // baseURL: "http://localhost:8005"
  baseURL: "https://central-server-8r2a.onrender.com"
})