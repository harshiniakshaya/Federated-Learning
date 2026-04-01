import axios from "axios"

export const hospitalA_local = axios.create({
  baseURL: "http://localhost:8001"
})

export const hospitalA_comm = axios.create({
  baseURL: "http://localhost:8002"
})

export const hospitalB_local = axios.create({
  baseURL: "http://localhost:8003"
})

export const hospitalB_comm = axios.create({
  baseURL: "http://localhost:8004"
})

export const central = axios.create({
  baseURL: "http://localhost:8005"
})