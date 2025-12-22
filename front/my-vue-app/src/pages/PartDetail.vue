<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { usePartsStore } from '../stores/parts'
import { useUserStore } from '../stores/user'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessage, ElTable, ElTableColumn, ElButton, ElTag, ElCard, ElDescriptions, ElDescriptionsItem, ElIcon, ElDialog, ElForm, ElFormItem, ElInputNumber, ElInput, ElRadioGroup, ElRadioButton } from 'element-plus'
import { Warning, Edit, Back } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const partsStore = usePartsStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { currentPart: part, transactions } = storeToRefs(partsStore)

const dialogVisible = ref(false)
const transactionForm = ref({
  type: 'in' as 'in' | 'out',
  quantity: 1,
  reason: ''
})
const submitting = ref(false)

onMounted(async () => {
  await userStore.fetchMe()
  const id = route.params.id as string
  await partsStore.getPart(id)
  await partsStore.fetchTransactions(id)
})

function canEdit() {
  // Assuming backend handles permission checks or we check against user site if needed
  return true
}

function goEdit() {
  if (!part.value) return
  router.push({ name: 'PartEdit', params: { id: part.value.id } })
}

function goBack() {
  router.back()
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

function openTransactionDialog(type: 'in' | 'out') {
  transactionForm.value = {
    type: type,
    quantity: 1,
    reason: ''
  }
  dialogVisible.value = true
}

async function submitTransaction() {
  if (!part.value) return
  
  submitting.value = true
  try {
    await partsStore.createTransaction({
      spare_part: part.value.id,
      transaction_type: transactionForm.value.type,
      quantity: transactionForm.value.quantity,
      reason: transactionForm.value.reason
    })
    ElMessage.success(transactionForm.value.type === 'in' ? '入库成功' : '出库成功')
    dialogVisible.value = false
  } catch (e: any) {
    console.error(e)
    ElMessage.error('操作失败: ' + (e.response?.data?.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="part" class="part-detail-container">
    <div class="header">
      <div class="title-section">
        <el-button :icon="Back" circle @click="goBack" style="margin-right: 12px" />
        <h2 style="margin: 0">
          {{ part.name }}
          <el-tag v-if="part.status === 'inactive'" type="info" style="margin-left: 8px">停用</el-tag>
        </h2>
      </div>
      <div class="actions">
        <el-button type="success" @click="openTransactionDialog('in')">入库</el-button>
        <el-button type="warning" @click="openTransactionDialog('out')">出库</el-button>
        <el-button v-if="canEdit()" type="primary" :icon="Edit" @click="goEdit">编辑备件</el-button>
      </div>
    </div>

    <el-alert
      v-if="part.alarmQty && part.quantity <= part.alarmQty"
      title="库存告警"
      type="error"
      description="当前库存已低于告警阈值，请及时补货！"
      show-icon
      style="margin-bottom: 20px"
    />

    <div class="content-grid">
      <div class="left-panel">
        <el-card shadow="never" class="image-card">
          <img 
            v-if="part.imageUrl" 
            :src="part.imageUrl" 
            class="part-image"
          />
          <div v-else class="no-image">暂无图片</div>
        </el-card>

        <el-card shadow="never" header="基本信息" style="margin-top: 20px">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="型号">{{ part.model || '-' }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ part.category?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="位置">{{ part.location || '-' }}</el-descriptions-item>
            <el-descriptions-item label="供应商">{{ part.supplier || '-' }}</el-descriptions-item>
            <el-descriptions-item label="供应商编码">{{ part.supplier_code || '-' }}</el-descriptions-item>
            <el-descriptions-item label="采购周期">{{ part.procurementDays ? part.procurementDays + ' 天' : '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>

      <div class="right-panel">
        <el-card shadow="never" header="库存状态">
          <div class="stock-info">
            <div class="stock-item">
              <div class="label">当前库存</div>
              <div class="value" :class="{ 'text-danger': part.alarmQty && part.quantity <= part.alarmQty }">
                {{ part.quantity }}
              </div>
            </div>
            <div class="stock-item">
              <div class="label">告警阈值</div>
              <div class="value">{{ part.alarmQty || '-' }}</div>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" header="出入库记录" style="margin-top: 20px">
          <el-table :data="transactions" style="width: 100%" max-height="400">
            <el-table-column prop="created_at" label="时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="transaction_type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.transaction_type === 'in' ? 'success' : 'warning'">
                  {{ row.transaction_type === 'in' ? '入库' : '出库' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="operator_name" label="操作人" width="100" />
            <el-table-column prop="reason" label="备注" min-width="120" show-overflow-tooltip />
          </el-table>
        </el-card>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="transactionForm.type === 'in' ? '备件入库' : '备件出库'"
      width="500px"
    >
      <el-form :model="transactionForm" label-width="80px">
        <el-form-item label="操作类型">
          <el-radio-group v-model="transactionForm.type">
            <el-radio-button label="in">入库</el-radio-button>
            <el-radio-button label="out">出库</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="transactionForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="transactionForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入出入库原因、用途等"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTransaction" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.part-detail-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.title-section {
  display: flex;
  align-items: center;
}
.content-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
}
.image-card {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.part-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.no-image {
  color: #909399;
  font-size: 14px;
}
.stock-info {
  display: flex;
  gap: 40px;
}
.stock-item .label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}
.stock-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.text-danger {
  color: #f56c6c;
}
</style>

