<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { usePartsStore } from '../stores/parts'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElTable, ElTableColumn, ElButton, ElInput, ElSelect, ElOption, ElPagination, ElIcon, ElMessageBox, ElMessage } from 'element-plus'
import { Search, Warning } from '@element-plus/icons-vue'

const partsStore = usePartsStore()
const userStore = useUserStore()
const router = useRouter()
const { parts, total, loading, categories, sites } = storeToRefs(partsStore)
const searchQuery = ref('')
const selectedCategory = ref<number | undefined>(undefined)
const selectedSite = ref<number | undefined>(undefined)
const selectedStatus = ref<string | undefined>(undefined)
const currentPage = ref(1)
const pageSize = ref(10)

// 批量删除相关
const isBatchDeleteMode = ref(false)
const selectedRows = ref<any[]>([])

const canCreate = computed(() => {
  const user = userStore.user
  if (!user) return false
  // Assuming backend handles permission checks, but frontend can hide button
  return true 
})

onMounted(async () => {
  try {
    await userStore.fetchMe()
  } catch (e) {
    // 未登录或token无效，不影响页面加载
  }
  
  if (userStore.user) {
    await initPageData()
  }
})

// 监听用户变化，登录后自动选中所属场站并刷新数据
watch(() => userStore.user, (newUser) => {
  if (newUser) {
    initPageData()
  } else {
    // 登出后，清空数据
    selectedSite.value = undefined
    parts.value = []
    total.value = 0
  }
})

async function initPageData() {
  await partsStore.fetchCategories()
  await partsStore.fetchSites()
  
  // 默认选中用户所属场站
  if (userStore.user?.site_id) {
    selectedSite.value = userStore.user.site_id
  }
  
  await loadParts()
}

async function loadParts() {
  if (!userStore.user) return
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

function handleSizeChange(val: number) {
  pageSize.value = val
  currentPage.value = 1
  loadParts()
}

function getAlarmStatus(qty: number, alarmQty: number = 0) {
  if (alarmQty && qty <= alarmQty) return 'alert'
  return 'normal'
}

function tableRowClassName({ row }: { row: any }) {
  if (row.alarmQty && row.quantity <= row.alarmQty) {
    return 'warning-row'
  }
  return ''
}

function goDetail(id: string | number) {
  router.push({ name: 'PartDetail', params: { id: String(id) } })
}

function toggleBatchDeleteMode() {
  isBatchDeleteMode.value = !isBatchDeleteMode.value
  selectedRows.value = []
}

function handleSelectionChange(val: any[]) {
  selectedRows.value = val
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 个备件吗？此操作不可恢复！`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 循环删除
    // 注意：实际项目中建议后端提供批量删除接口
    let successCount = 0
    for (const row of selectedRows.value) {
      try {
        await partsStore.deletePart(row.id)
        successCount++
      } catch (e) {
        console.error(`Failed to delete part ${row.id}`, e)
      }
    }
    
    ElMessage.success(`成功删除 ${successCount} 个备件`)
    isBatchDeleteMode.value = false
    selectedRows.value = []
    await loadParts()
    
  } catch (e) {
    // Cancelled
  }
}
</script>

<template>
  <div class="parts-list-container">
    <div class="header-actions">
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
          v-model="selectedSite" 
          placeholder="场站" 
          clearable 
          @change="handleSearch" 
          style="width: 150px"
        >
          <el-option label="所有场站" :value="''" />
          <el-option v-for="s in sites" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>

        <el-select v-model="selectedCategory" placeholder="分类" clearable @change="handleSearch" style="width: 150px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>

        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      
      <div class="action-buttons">
        <el-button 
          v-if="isBatchDeleteMode" 
          type="danger" 
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          删除选中 ({{ selectedRows.length }})
        </el-button>
        
        <el-button 
          :type="isBatchDeleteMode ? 'info' : 'danger'" 
          plain
          @click="toggleBatchDeleteMode"
        >
          {{ isBatchDeleteMode ? '取消批量' : '批量删除' }}
        </el-button>

        <el-button v-if="canCreate" type="success" @click="router.push({ name: 'PartCreate' })">
          新增备件
        </el-button>
      </div>
    </div>

    <el-table 
      :data="parts" 
      v-loading="loading" 
      style="width: 100%; margin-top: 20px" 
      border
      :row-class-name="tableRowClassName"
      @selection-change="handleSelectionChange"
    >
      <el-table-column v-if="isBatchDeleteMode" type="selection" width="55" />
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
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="goDetail(row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 20px; display: flex; justify-content: flex-end">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
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
:deep(.el-table .warning-row) {
  --el-table-tr-bg-color: var(--el-color-danger-light-9);
}
:deep(.el-table .warning-row:hover > td.el-table__cell) {
  background-color: var(--el-color-danger-light-8) !important;
}
</style>