import { defineStore } from 'pinia'
import { partsApi, type SparePart, type Category, type Transaction, type SparePartFilter, type Site } from '../services/partsApi'
import { logger } from '../utils/logger'

export type Part = SparePart

export const usePartsStore = defineStore('parts', {
  state: () => ({
    parts: [] as Part[],
    categories: [] as Category[],
    sites: [] as Site[],
    currentPart: null as Part | null,
    transactions: [] as Transaction[],
    total: 0,
    loading: false
  }),
  actions: {
    async fetchSites() {
      const res = await partsApi.getSites()
      const data = res.data || res
      if (Array.isArray(data)) {
        this.sites = data
      } else if (data.results) {
        this.sites = data.results
      }
      return this.sites
    },
    async fetchParts(params: SparePartFilter = {}) {
      this.loading = true
      try {
        const res = await partsApi.getSpareParts(params)
        logger.log('fetchParts raw response:', res) // Debug log 1
        
        // Assuming backend returns { code: 0, data: { results: [], count: 0 } }
        const data = res.data || res
        logger.log('fetchParts processed data:', data) // Debug log 2

        if (data.items) { // Check for 'items' first as per your backend response structure
            this.parts = data.items
            this.total = data.total || data.items.length
        } else if (data.results) {
            this.parts = data.results
            this.total = data.count || data.results.length
        } else if (Array.isArray(data)) {
            this.parts = data
            this.total = data.length
        } else {
            this.parts = []
            this.total = 0
        }
        logger.log('fetchParts final state:', { parts: this.parts, total: this.total }) // Debug log 3
        return this.parts
      } finally {
        this.loading = false
      }
    },
    async fetchCategories() {
      const res = await partsApi.getCategories()
      const data = res.data || res
      if (Array.isArray(data)) {
        this.categories = data
      } else if (data.results) {
        this.categories = data.results
      }
      return this.categories
    },
    async getPart(id: string | number) {
      this.loading = true
      try {
        const res = await partsApi.getSparePart(id)
        this.currentPart = res.data || res
        return this.currentPart
      } finally {
        this.loading = false
      }
    },
    async createPart(data: Partial<Part> | FormData) {
      const res = await partsApi.createSparePart(data)
      return res.data || res
    },
    async updatePart(id: string | number, data: Partial<Part> | FormData) {
      const res = await partsApi.updateSparePart(id, data)
      return res.data || res
    },
    async deletePart(id: string | number) {
      await partsApi.deleteSparePart(id)
      this.parts = this.parts.filter(p => p.id !== id)
      return true
    },
    async fetchTransactions(sparePartId: string | number) {
        const res = await partsApi.getTransactionsByPart(sparePartId)
        const data = res.data || res
        if (data.items) {
            this.transactions = data.items
        } else if (data.results) {
            this.transactions = data.results
        } else if (Array.isArray(data)) {
            this.transactions = data
        }
        return this.transactions
    },
    async createTransaction(data: any) {
      const res = await partsApi.createTransaction(data)
      // Refresh part and transactions
      if (data.spare_part) {
        await this.getPart(data.spare_part)
        await this.fetchTransactions(data.spare_part)
      }
      return res.data || res
    }
  }
})
