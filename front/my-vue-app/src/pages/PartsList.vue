<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { usePartsStore } from '../stores/parts'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElTable, ElTableColumn, ElButton, ElInput, ElSelect, ElOption, ElPagination, ElIcon } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const partsStore = usePartsStore()
const userStore = useUserStore()
const router = useRouter()
const { parts, total, loading, categories, sites } = storeToRefs(partsStore)
const searchQuery = ref('')
const selectedCategory = ref<number | undefined>(undefined)
const selectedSite = ref<number | undefined>(undefined)
const selectedStatus = ref<string | undefined>(undefined)
const currentPage = ref(1)
const pageSize = ref(20)

const canCreate = computed(() => {
  const user = userStore.user
  if (!user) return false
  // Assuming backend handles permission checks, but frontend can hide button
  return true 
})

onMounted(async () => {
  await userStore.fetchMe()
  await partsStore.fetchCategories()
  await partsStore.fetchSites()
  
  // 默认选中用户所属场站
  if (userStore.user?.site_id) {
    selectedSite.value = userStore.user.site_id
  }
  
  await loadParts()
})

async function loadParts() {
  await partsStore.fetchParts({
    page: currentPage.value,
    limit: pageSize.value,
    search: searchQuery.value,
    category_id: selectedCategory.value,
    site_id: selectedSite.value,
    status: selectedStatus.value
  })
  console.log('PartsList received parts:', parts.value)
}

function handleSearch() {
  currentPage.value = 1
  loadParts()
}

function handlePageChange(page: number) {
  currentPage.value = page
  loadParts()
}

function getAlarmStatus(qty: number, alarmQty: number = 0) {
  if (alarmQty && qty <= alarmQty) return 'alert'
  return 'normal'
}

function goDetail(id: string | number) {
  router.push({ name: 'PartDetail', params: { id: String(id) } })
}

function goEdit(id: string | number) {
  router.push({ name: 'PartEdit', params: { id: String(id) } })
}

async function handleDelete(id: string | number) {
  if (!confirm('确定删除该备件吗？')) return
  await partsStore.deletePart(id)
  await loadParts()
}
</script>

<template>
  <div class="parts-list-container">
    <div class="header-actions">
      <!-- Debug Info -->
      <!-- <div v-if="true" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px; font-size: 12px;">
        <strong>Debug Info:</strong>
        Loading: {{ loading }} | 
        Total: {{ total }} | 
        Parts Length: {{ parts ? parts.length : 'null' }}
        <br>
        First Part: {{ parts && parts.length > 0 ? JSON.stringify(parts[0]) : 'None' }}
      </div> -->

      <div class="filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索备件名称/型号"
          style="width: 200px"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select 
          v-if="userStore.user?.can_view_all_sites"
          v-model="selectedSite" 
          placeholder="场站" 
          clearable 
          @change="handleSearch" 
          style="width: 150px"
        >
          <el-option v-for="s in sites" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>

        <el-select v-model="selectedCategory" placeholder="分类" clearable @change="handleSearch" style="width: 150px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>

        <el-select v-model="selectedStatus" placeholder="状态" clearable @change="handleSearch" style="width: 120px">
          <el-option label="正常" value="normal" />
          <el-option label="停用" value="inactive" />
        </el-select>

        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      
      <el-button v-if="canCreate" type="success" @click="router.push({ name: 'PartCreate' })">
        新增备件
      </el-button>
    </div>

    <el-table :data="parts" v-loading="loading" style="width: 100%; margin-top: 20px" border>
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="model" label="型号" min-width="100" />
      <el-table-column prop="stationName" label="所属场站" min-width="120" />
      <el-table-column prop="category.name" label="分类" width="100" />
      <el-table-column prop="location" label="位置" min-width="120" />
      <el-table-column label="库存" width="120">
        <template #default="{ row }">
          <span :style="{ color: getAlarmStatus(row.quantity, row.alarmQty) === 'alert' ? 'red' : 'inherit', fontWeight: getAlarmStatus(row.quantity, row.alarmQty) === 'alert' ? 'bold' : 'normal' }">
            {{ row.quantity }}
            <el-icon v-if="getAlarmStatus(row.quantity, row.alarmQty) === 'alert'"><Warning /></el-icon>
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="alarmQty" label="告警阈值" width="100" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="goDetail(row.id)">详情</el-button>
          <el-button link type="primary" @click="goEdit(row.id)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 20px; display: flex; justify-content: flex-end">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.parts-list-container {
  padding: 20px;
}
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
.filters {
  display: flex;
  gap: 10px;
}
</style>