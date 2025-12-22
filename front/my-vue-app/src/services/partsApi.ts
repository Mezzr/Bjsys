import api from './api'

export interface Category {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
}

export interface SparePart {
  id: number
  name: string
  model?: string
  description?: string
  location?: string
  supplier?: string
  supplier_code?: string
  quantity: number
  alarmQty?: number
  procurementDays?: number
  categoryId?: number
  category?: Category // For display
  status?: string
  site?: string 
  stationName?: string // Added
  imageUrl?: string
  created_at?: string
  updated_at?: string
}

export interface Transaction {
  id: number
  spare_part: number | SparePart
  transaction_type: 'IN' | 'OUT'
  quantity: number
  reason?: string
  operator?: string // User name
  created_at: string
  price?: number
}

export interface TransactionFilter {
  spare_part_id?: number
  transaction_type?: 'IN' | 'OUT'
  start_date?: string
  end_date?: string
  page?: number
  limit?: number
}

export interface SparePartFilter {
  category_id?: number
  site_id?: number // Added
  status?: string
  search?: string
  page?: number
  limit?: number
}

export interface Site {
  id: number
  name: string
  code: string
}

export const partsApi = {
  // Sites
  getSites: () => api.get('/sites/'),

  // Categories
  getCategories: () => api.get('/categories/'),
  createCategory: (data: Partial<Category>) => api.post('/categories/', data),

  // Spare Parts
  getSpareParts: (params: SparePartFilter) => api.get('/spare-parts/', { params }),
  createSparePart: (data: Partial<SparePart>) => api.post('/spare-parts/', data),
  getSparePart: (id: number | string) => api.get(`/spare-parts/${id}/`),
  updateSparePart: (id: number | string, data: Partial<SparePart>) => api.patch(`/spare-parts/${id}/`, data),
  deleteSparePart: (id: number | string) => api.delete(`/spare-parts/${id}/`),

  // Transactions
  getTransactions: (params: TransactionFilter) => api.get('/transactions/', { params }),
  createTransaction: (data: any) => api.post('/transactions/', data),
  getTransactionsByPart: (sparePartId: number | string, params?: any) => api.get('/transactions/by_spare_part', { params: { spare_part_id: sparePartId, ...params } }),
  getTransactionStatistics: (sparePartId?: number | string) => api.get('/transactions/statistics/', { params: { spare_part_id: sparePartId } }),
}
